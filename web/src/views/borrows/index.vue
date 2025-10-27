<script setup lang="tsx">
import { ElButton, ElPopconfirm, ElTag } from 'element-plus';
import { fetchGetBorrowList, fetchReturnBook, fetchRenewBook } from '@/service/api';
import { useTable } from '@/hooks/common/table';
import { $t } from '@/locales';
import { useAuthStore } from '@/store/modules/auth';
import { ref } from 'vue';

const authStore = useAuthStore();
const renewingIds = ref<Set<number>>(new Set());
const returningIds = ref<Set<number>>(new Set());

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
  apiFn: fetchGetBorrowList,
  apiParams: {
    current: 1,
    size: 10,
    user_id: authStore.userInfo.userId, // 只查询当前用户的借阅记录
    book_id: undefined,
    status: undefined,
    search: undefined,
    overdue_only: false
  },
  columns: () => [
    { prop: 'index', label: $t('common.index'), width: 64 },
    {
      prop: 'book_title',
      label: '图书信息',
      minWidth: 250,
      formatter: row => (
        <div>
          <div class="font-medium text-base">{row.book_title}</div>
          <div class="text-sm text-gray-500 mt-1">
            <span>作者：{row.book_author}</span>
            <span class="ml-4">ISBN：{row.book_isbn}</span>
          </div>
        </div>
      )
    },
    {
      prop: 'borrow_date',
      label: '借阅日期',
      width: 120,
      formatter: row => new Date(row.borrow_date).toLocaleDateString('zh-CN')
    },
    {
      prop: 'due_date',
      label: '到期日期',
      width: 120,
      formatter: row => {
        const dueDate = new Date(row.due_date);
        const isOverdue = row.status === 'overdue' || (new Date() > dueDate && row.status === 'borrowed');
        return (
          <span class={isOverdue ? 'text-red-500 font-medium' : ''}>
            {dueDate.toLocaleDateString('zh-CN')}
          </span>
        );
      }
    },
    {
      prop: 'return_date',
      label: '归还日期',
      width: 120,
      formatter: row => row.return_date ? new Date(row.return_date).toLocaleDateString('zh-CN') : '-'
    },
    {
      prop: 'status',
      label: '状态',
      width: 100,
      formatter: row => {
        const statusConfig = {
          borrowed: { type: 'primary', text: '借阅中' },
          returned: { type: 'success', text: '已归还' },
          overdue: { type: 'danger', text: '逾期' },
          renewed: { type: 'warning', text: '已续借' }
        };
        const config = statusConfig[row.status] || { type: 'info', text: '未知' };
        return <ElTag type={config.type}>{config.text}</ElTag>;
      }
    },
    {
      prop: 'renewal_count',
      label: '续借次数',
      width: 100,
      formatter: row => (
        <span class={row.renewal_count >= 2 ? 'text-orange-500' : ''}>
          {row.renewal_count || 0}次
          {row.renewal_count >= 2 && <span class="text-xs ml-1">(已达上限)</span>}
        </span>
      )
    },
    {
      prop: 'days_overdue',
      label: '逾期情况',
      width: 100,
      formatter: row => {
        if (row.days_overdue > 0) {
          return (
            <div>
              <ElTag type="danger">{row.days_overdue}天</ElTag>
              {row.fine_amount > 0 && (
                <div class="text-xs text-red-500 mt-1">罚金: ¥{row.fine_amount}</div>
              )}
            </div>
          );
        }
        return <span class="text-green-500">正常</span>;
      }
    },
    {
      prop: 'operate',
      label: '操作',
      width: 180,
      formatter: row => (
        <div class="flex justify-center items-center gap-2">
          {row.status === 'borrowed' || row.status === 'overdue' ? (
            <>
              <ElPopconfirm
                title="确认要归还这本图书吗？"
                onConfirm={() => handleReturn(row.id)}
              >
                {{
                  reference: () => (
                    <ElButton
                      type="success"
                      size="small"
                      loading={returningIds.value.has(row.id)}
                      disabled={returningIds.value.has(row.id)}
                    >
                      {returningIds.value.has(row.id) ? '归还中...' : '归还'}
                    </ElButton>
                  )
                }}
              </ElPopconfirm>
              {(row.renewal_count || 0) < 2 && (
                <ElPopconfirm
                  title="确认要续借这本图书吗？续借期限为30天。"
                  onConfirm={() => handleRenew(row.id)}
                >
                  {{
                    reference: () => (
                      <ElButton
                        type="warning"
                        size="small"
                        loading={renewingIds.value.has(row.id)}
                        disabled={renewingIds.value.has(row.id)}
                      >
                        {renewingIds.value.has(row.id) ? '续借中...' : '续借'}
                      </ElButton>
                    )
                  }}
                </ElPopconfirm>
              )}
            </>
          ) : (
            <span class="text-gray-400">无可用操作</span>
          )}
        </div>
      )
    }
  ]
});

async function handleReturn(borrowId: number) {
  returningIds.value.add(borrowId);
  try {
    await fetchReturnBook(borrowId);
    window.$message?.success('图书归还成功！');
    getDataByPage();
  } catch (error) {
    window.$message?.error('归还失败，请稍后重试');
  } finally {
    returningIds.value.delete(borrowId);
  }
}

async function handleRenew(borrowId: number) {
  renewingIds.value.add(borrowId);
  try {
    await fetchRenewBook(borrowId, { renewal_days: 30 });
    window.$message?.success('续借成功！已延长30天借阅期限');
    getDataByPage();
  } catch (error) {
    window.$message?.error('续借失败，请稍后重试');
  } finally {
    renewingIds.value.delete(borrowId);
  }
}

// 筛选条件
function filterByStatus(status: string) {
  searchParams.status = status === 'all' ? undefined : status;
  getDataByPage();
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <!-- 快捷筛选 -->
    <ElCard>
      <div class="flex items-center gap-4">
        <span class="text-sm font-medium">快捷筛选：</span>
        <ElButton
          size="small"
          :type="!searchParams.status ? 'primary' : 'default'"
          @click="filterByStatus('all')"
        >
          全部记录
        </ElButton>
        <ElButton
          size="small"
          :type="searchParams.status === 'borrowed' ? 'primary' : 'default'"
          @click="filterByStatus('borrowed')"
        >
          借阅中
        </ElButton>
        <ElButton
          size="small"
          :type="searchParams.status === 'overdue' ? 'danger' : 'default'"
          @click="filterByStatus('overdue')"
        >
          逾期未还
        </ElButton>
        <ElButton
          size="small"
          :type="searchParams.status === 'returned' ? 'success' : 'default'"
          @click="filterByStatus('returned')"
        >
          已归还
        </ElButton>
      </div>
    </ElCard>

    <ElCard class="sm:flex-1-hidden card-wrapper" body-class="ht50">
      <template #header>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-lg font-semibold">我的借阅记录</p>
            <p class="text-sm text-gray-500 mt-1">管理您的图书借阅、续借和归还</p>
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
          empty-text="暂无借阅记录"
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
