<script setup lang="tsx">
import { ElButton, ElTag, ElPopconfirm } from 'element-plus';
import { enableStatusRecord } from '@/constants/business';
import { fetchGetBookList, fetchBorrowBook } from '@/service/api';
import { useTable } from '@/hooks/common/table';
import { $t } from '@/locales';
import BookSearch from './modules/book-search.vue';
import { ref } from 'vue';
import { useAuthStore } from '@/store/modules/auth';

const authStore = useAuthStore();
const borrowingIds = ref<Set<number>>(new Set());

const {
  columns,
  columnChecks,
  data,
  loading,
  getData,
  getDataByPage,
  mobilePagination,
  searchParams,
  resetSearchParams
} = useTable({
  apiFn: fetchGetBookList,
  apiParams: {
    current: 1,
    size: 10,
    title: undefined,
    author: undefined,
    publisher: undefined,
    category: undefined,
    isbn: undefined
  },
  columns: () => [
    { prop: 'index', label: $t('common.index'), width: 64 },
    { prop: 'title', label: '书名', minWidth: 150 },
    { prop: 'author', label: '作者', minWidth: 120 },
    { prop: 'isbn', label: 'ISBN', minWidth: 120 },
    { prop: 'publisher', label: '出版社', minWidth: 120 },
    { prop: 'category', label: '分类', width: 100 },
    { prop: 'price', label: '价格', width: 80, formatter: row => `¥${row.price}` },
    {
      prop: 'stock_quantity',
      label: '库存',
      width: 80,
      formatter: row => (
        <ElTag type={row.stock_quantity > 0 ? 'success' : 'danger'}>
          {row.stock_quantity > 0 ? `剩余${row.stock_quantity}本` : '暂无库存'}
        </ElTag>
      )
    },
    {
      prop: 'publish_date',
      label: '出版日期',
      width: 100,
      formatter: row => row.publish_date
    },
    {
      prop: 'operate',
      label: '操作',
      width: 120,
      formatter: row => (
        <div class="flex-center">
          {row.stock_quantity > 0 ? (
            <ElPopconfirm
              title="确认要借阅这本图书吗？"
              onConfirm={() => handleBorrow(row.id)}
            >
              {{
                reference: () => (
                  <ElButton
                    type="primary"
                    size="small"
                    loading={borrowingIds.value.has(row.id)}
                    disabled={borrowingIds.value.has(row.id)}
                  >
                    {borrowingIds.value.has(row.id) ? '借阅中...' : '借阅'}
                  </ElButton>
                )
              }}
            </ElPopconfirm>
          ) : (
            <ElButton type="info" size="small" disabled>
              无库存
            </ElButton>
          )}
        </div>
      )
    }
  ]
});

async function handleBorrow(bookId: number) {
  borrowingIds.value.add(bookId);

  try {
    // 构造借阅参数对象
    const borrowData: Api.SystemManage.BorrowCreateParams = {
      book_id: bookId
      // user_id: authStore.userInfo.userId, // 从当前登录用户获取
      // 可以根据需要添加其他参数，如借阅期限等
    };

    await fetchBorrowBook(borrowData);
    window.$message?.success('借阅成功！');
    // 刷新数据以更新库存
    getDataByPage();
  } catch (error) {
    window.$message?.error('借阅失败，请稍后重试');
  } finally {
    borrowingIds.value.delete(bookId);
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <BookSearch v-model:model="searchParams" @reset="resetSearchParams" @search="getDataByPage" />
    <ElCard class="sm:flex-1-hidden card-wrapper" body-class="ht50">
      <template #header>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-lg font-semibold">图书借阅</p>
            <p class="text-sm text-gray-500 mt-1">浏览并借阅您感兴趣的图书</p>
          </div>
          <div class="flex items-center gap-2">
            <ElButton @click="getData" :loading="loading">
              刷新列表
            </ElButton>
          </div>
        </div>
      </template>
      <div class="h-[calc(100%-50px)]">
        <ElTable
          v-loading="loading"
          height="100%"
          border
          class="sm:h-full"
          :data="data"
          row-key="id"
        >
          <ElTableColumn v-for="col in columns" :key="col.prop" v-bind="col" />
        </ElTable>
        <div class="mt-20px flex justify-end">
          <ElPagination
            v-if="mobilePagination.total"
            layout="total,prev,pager,next,sizes"
            v-bind="mobilePagination"
            @current-change="mobilePagination['current-change']"
            @size-change="mobilePagination['size-change']"
          />
        </div>
      </div>
    </ElCard>
  </div>
</template>

<style lang="scss" scoped>
:deep(.el-card) {
  .ht50 {
    height: calc(100% - 50px);
  }
}
</style>
