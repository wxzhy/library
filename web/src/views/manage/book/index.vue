<script setup lang="tsx">
import { ElButton, ElPopconfirm, ElTag } from 'element-plus';
import { enableStatusRecord } from '@/constants/business';
import { fetchGetBookList, fetchDeleteBook, fetchBatchDeleteBooks } from '@/service/api';
import { useTable, useTableOperate } from '@/hooks/common/table';
import { $t } from '@/locales';
import BookOperateDrawer from './modules/book-operate-drawer.vue';
import BookSearch from './modules/book-search.vue';

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
    { type: 'selection', width: 48 },
    { prop: 'index', label: $t('common.index'), width: 64 },
    { prop: 'title', label: '书名', minWidth: 150 },
    { prop: 'author', label: '作者', minWidth: 120 },
    { prop: 'isbn', label: 'ISBN', minWidth: 120 },
    { prop: 'publisher', label: '出版社', minWidth: 120 },
    { prop: 'category', label: '分类', width: 100 },
    { prop: 'price', label: '价格', width: 80, formatter: row => `¥${row.price}` },
    { prop: 'stock_quantity', label: '库存', width: 80 },
    {
      prop: 'publish_date',
      label: '出版日期',
      width: 100,
      formatter: row => row.publish_date
    },
    {
      prop: 'operate',
      label: $t('common.operate'),
      width: 130,
      formatter: row => (
        <div class="flex-center">
          <ElButton type="primary" plain size="small" onClick={() => edit(row.id)}>
            {$t('common.edit')}
          </ElButton>
          <ElPopconfirm title={$t('common.confirmDelete')} onConfirm={() => handleDelete(row.id)}>
            {{
              reference: () => (
                <ElButton type="danger" plain size="small">
                  {$t('common.delete')}
                </ElButton>
              )
            }}
          </ElPopconfirm>
        </div>
      )
    }
  ]
});

const {
  drawerVisible,
  operateType,
  editingData,
  handleAdd,
  handleEdit,
  checkedRowKeys,
  onBatchDeleted,
  onDeleted
} = useTableOperate(data, getData);

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    window.$message?.warning('请选择要删除的图书');
    return;
  }

  try {
    const ids = checkedRowKeys.value.map(item => item.id);
    await fetchBatchDeleteBooks(ids);
    // window.$message?.success('批量删除成功');
    onBatchDeleted();
  } catch (error) {
    window.$message?.error('批量删除失败');
  }
}

async function handleDelete(id: number) {
  try {
    await fetchDeleteBook(id);
    // window.$message?.success('删除成功');
    onDeleted();
  } catch (error) {
    window.$message?.error('删除失败');
  }
}

function edit(id: number) {
  handleEdit(id);
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <BookSearch v-model:model="searchParams" @reset="resetSearchParams" @search="getDataByPage" />
    <ElCard class="sm:flex-1-hidden card-wrapper" body-class="ht50">
      <template #header>
        <div class="flex items-center justify-between">
          <p>图书管理</p>
          <TableHeaderOperation
            v-model:columns="columnChecks"
            :disabled-delete="checkedRowKeys.length === 0"
            :loading="loading"
            @add="handleAdd"
            @delete="handleBatchDelete"
            @refresh="getData"
          />
        </div>
      </template>
      <div class="h-[calc(100%-50px)] flex flex-col">
        <ElTable
          v-loading="loading"
          class="flex-1"
          border
          :data="data"
          row-key="id"
          @selection-change="checkedRowKeys = $event"
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
      <BookOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getDataByPage"
      />
    </ElCard>
  </div>
</template>

<style lang="scss" scoped>
:deep(.el-card) {
  .ht50 {ht50 {
    height: calc(100% - 50px);   height: calc(100% - 50px);
  }
}}
</style>
