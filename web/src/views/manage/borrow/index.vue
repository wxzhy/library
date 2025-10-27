<script setup lang="tsx">
import { ElButton, ElPopconfirm, ElTag } from 'element-plus';
import { fetchGetBorrowList, fetchReturnBook, fetchRenewBook } from '@/service/api';
import { useTable, useTableOperate } from '@/hooks/common/table';
import { $t } from '@/locales';
import BorrowOperateDrawer from './modules/borrow-operate-drawer.vue';
import BorrowSearch from './modules/borrow-search.vue';

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
    user_id: undefined,
    book_id: undefined,
    status: undefined,
    search: undefined,
    overdue_only: false
  },
  columns: () => [
    { type: 'selection', width: 48 },
    { prop: 'index', label: $t('common.index'), width: 64 },
    {
      prop: 'user_name',
      label: '借阅用户',
      minWidth: 120,
      formatter: row => (
        <div>
          <div>{row.user_name}</div>
          <div class="text-xs text-gray-500">{row.user_email}</div>
        </div>
      )
    },
    {
      prop: 'book_title',
      label: '图书信息',
      minWidth: 200,
      formatter: row => (
        <div>
          <div class="font-medium">{row.book_title}</div>
          <div class="text-xs text-gray-500">{row.book_author} · {row.book_isbn}</div>
        </div>
      )
    },
    {
      prop: 'borrow_date',
      label: '借阅日期',
      width: 100,
      formatter: row => new Date(row.borrow_date).toLocaleDateString()
    },
    {
      prop: 'due_date',
      label: '到期日期',
      width: 100,
      formatter: row => new Date(row.due_date).toLocaleDateString()
    },
    {
      prop: 'return_date',
      label: '归还日期',
      width: 100,
      formatter: row => row.return_date ? new Date(row.return_date).toLocaleDateString() : '-'
    },
    {
      prop: 'status',
      label: '状态',
      width: 80,
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
      width: 80,
      formatter: row => row.renewal_count || 0
    },
    {
      prop: 'fine_amount',
      label: '罚金',
      width: 80,
      formatter: row => row.fine_amount > 0 ? `¥${row.fine_amount}` : '-'
    },
    {
      prop: 'days_overdue',
      label: '逾期天数',
      width: 80,
      formatter: row => row.days_overdue > 0 ? (
        <ElTag type="danger">{row.days_overdue}天</ElTag>
      ) : '-'
    },
    {
      prop: 'operate',
      label: $t('common.operate'),
      width: 130,
      formatter: row => (
        <div class="flex-center">
          {row.status === 'borrowed' && (
            <>
              <ElButton
                type="success"
                plain
                size="small"
                onClick={() => handleReturn(row.id)}
              >
                归还
              </ElButton>
              <ElButton
                type="warning"
                plain
                size="small"
                onClick={() => handleRenew(row.id)}
              >
                续借
              </ElButton>
            </>
          )}
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
  onDeleted
} = useTableOperate(data, getData);

async function handleReturn(borrowId: number) {
  try {
    await fetchReturnBook(borrowId);
    window.$message?.success('归还成功');
    getDataByPage(); // 刷新当前页数据
  } catch (error) {
    window.$message?.error('归还失败');
  }
}

async function handleRenew(borrowId: number) {
  try {
    await fetchRenewBook(borrowId, { renewal_days: 30 });
    window.$message?.success('续借成功');
    getDataByPage(); // 刷新当前页数据
  } catch (error) {
    window.$message?.error('续借失败');
  }
}

function viewDetail(borrowId: number) {
  handleEdit(borrowId);
}

function handleBorrow() {
  handleAdd();
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <BorrowSearch v-model:model="searchParams" @reset="resetSearchParams" @search="getDataByPage" />
    <ElCard class="sm:flex-1-hidden card-wrapper" body-class="ht50">
      <template #header>
        <div class="flex items-center justify-between">
          <p>借阅管理</p>
          <div class="flex items-center gap-2">
            <TableHeaderOperation
              v-model:columns="columnChecks"
              :loading="loading"
              :show-add="false"
              :show-delete="false"
              @refresh="getData"
            />
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
      <BorrowOperateDrawer
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
  .ht50 {
    height: calc(100% - 50px);
  }
}
</style>
