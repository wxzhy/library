<script setup lang="tsx">
import { ElButton, ElPopconfirm, ElTag, ElDialog, ElForm, ElFormItem, ElInput } from 'element-plus';
import { fetchGetUserList, fetchDeleteUser, fetchBatchDeleteUsers, resetUserPassword } from '@/service/api';
import { $t } from '@/locales';
import { useTable, useTableOperate } from '@/hooks/common/table';
import { ref, reactive } from 'vue';
import UserOperateDrawer from './modules/user-operate-drawer.vue';
import UserSearch from './modules/user-search.vue';

defineOptions({ name: 'UserManage' });

// 添加密码重置相关的状态
const resetPasswordVisible = ref(false);
const resetPasswordLoading = ref(false);
const resetPasswordForm = reactive({
  userId: null as number | null,
  userName: '',
  newPassword: '',
  confirmPassword: ''
});

const {
  columns,
  columnChecks,
  data,
  getData,
  getDataByPage,
  loading,
  mobilePagination,
  searchParams,
  resetSearchParams
} = useTable({
  apiFn: fetchGetUserList,
  showTotal: true,
  apiParams: {
    current: 1,
    size: 10,
    search: undefined,
    is_active: undefined,
    is_admin: undefined
  },
  columns: () => [
    { type: 'selection', width: 48 },
    { prop: 'index', label: $t('common.index'), width: 64 },
    { prop: 'username', label: $t('page.manage.user.userName'), minWidth: 100 },
    { prop: 'full_name', label: '姓名', minWidth: 120 },
    { prop: 'phone', label: $t('page.manage.user.userPhone'), width: 120 },
    { prop: 'email', label: $t('page.manage.user.userEmail'), minWidth: 200 },
    {
      prop: 'is_active',
      label: $t('page.manage.user.userStatus'),
      align: 'center',
      formatter: row => {
        if (row.is_active === undefined) {
          return '';
        }
        const tagMap = {
          true: 'success',
          false: 'warning'
        };
        const label = row.is_active ? '启用' : '禁用';
        return <ElTag type={tagMap[row.is_active]}>{label}</ElTag>;
      }
    },
    {
      prop: 'is_admin',
      label: '管理员',
      align: 'center',
      formatter: row => {
        const tagMap = {
          true: 'warning',
          false: 'info'
        };
        const label = row.is_admin ? '是' : '否';
        return <ElTag type={tagMap[row.is_admin]}>{label}</ElTag>;
      }
    },
    {
      prop: 'created_at',
      label: '创建时间',
      width: 180,
      formatter: row => {
        return row.created_at ? new Date(row.created_at).toLocaleString() : '';
      }
    },
    {
      prop: 'operate',
      label: $t('common.operate'),
      align: 'center',
      width: 220,
      formatter: row => (
        <div class="flex-center gap-2">
          <ElButton type="primary" plain size="small" onClick={() => edit(row.id)}>
            {$t('common.edit')}
          </ElButton>
          <ElButton
            type="warning"
            plain
            size="small"
            onClick={() => openResetPasswordDialog(row)}
          >
            重置密码
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

// 打开重置密码对话框
function openResetPasswordDialog(row: any) {
  resetPasswordForm.userId = row.id;
  resetPasswordForm.userName = row.username;
  resetPasswordForm.newPassword = '';
  resetPasswordForm.confirmPassword = '';
  resetPasswordVisible.value = true;
}

// 关闭重置密码对话框
function closeResetPasswordDialog() {
  resetPasswordVisible.value = false;
  resetPasswordForm.userId = null;
  resetPasswordForm.userName = '';
  resetPasswordForm.newPassword = '';
  resetPasswordForm.confirmPassword = '';
}

// 提交重置密码
async function handleResetPasswordSubmit() {
  // 验证密码
  if (!resetPasswordForm.newPassword) {
    window.$message?.error('请输入新密码');
    return;
  }

  if (resetPasswordForm.newPassword.length < 6) {
    window.$message?.error('密码长度不能少于6位');
    return;
  }

  if (resetPasswordForm.newPassword !== resetPasswordForm.confirmPassword) {
    window.$message?.error('两次输入的密码不一致');
    return;
  }

  resetPasswordLoading.value = true;

  try {
    await resetUserPassword(resetPasswordForm.userId!, resetPasswordForm.newPassword);
    window.$message?.success('密码重置成功');
    closeResetPasswordDialog();
  } catch (error) {
    console.error('重置密码失败:', error);
    window.$message?.error('重置密码失败');
  } finally {
    resetPasswordLoading.value = false;
  }
}

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    window.$message?.warning('请选择要删除的用户');
    return;
  }

  try {
    const userIds = checkedRowKeys.value.map(item => item.id as number);
    await fetchBatchDeleteUsers(userIds);
    // window.$message?.success('批量删除成功');
    onBatchDeleted();
  } catch (error) {
    console.error('批量删除失败:', error);
    window.$message?.error('批量删除失败');
  }
}

async function handleDelete(id: number) {
  try {
    await fetchDeleteUser(id);
    onDeleted();
    // window.$message?.success('删除成功');
  } catch (error) {
    console.error('删除失败:', error);
    window.$message?.error('删除失败');
  }
}

function edit(id: number) {
  handleEdit(id);
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <UserSearch v-model:model="searchParams" @reset="resetSearchParams" @search="getDataByPage" />
    <ElCard class="sm:flex-1-hidden card-wrapper" body-class="ht50">
      <template #header>
        <div class="flex items-center justify-between">
          <p>{{ $t('page.manage.user.title') }}</p>
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
      </div>
      <div class="mt-20px flex justify-end">
        <ElPagination
          v-if="mobilePagination.total"
          layout="total,prev,pager,next,sizes"
          v-bind="mobilePagination"
          @current-change="mobilePagination['current-change']"
          @size-change="mobilePagination['size-change']"
        />
      </div>

      <!-- 用户操作抽屉 -->
      <UserOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getDataByPage"
      />

      <!-- 重置密码对话框 -->
      <ElDialog
        v-model="resetPasswordVisible"
        title="重置用户密码"
        width="400px"
        :before-close="closeResetPasswordDialog"
      >
        <ElForm label-width="80px">
          <ElFormItem label="用户名">
            <ElInput v-model="resetPasswordForm.userName" disabled />
          </ElFormItem>
          <ElFormItem label="新密码" required>
            <ElInput
              v-model="resetPasswordForm.newPassword"
              type="password"
              placeholder="请输入新密码(至少6位)"
              show-password
            />
          </ElFormItem>
          <ElFormItem label="确认密码" required>
            <ElInput
              v-model="resetPasswordForm.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
              show-password
            />
          </ElFormItem>
        </ElForm>

        <template #footer>
          <div class="flex justify-end gap-3">
            <ElButton @click="closeResetPasswordDialog">取消</ElButton>
            <ElButton
              type="primary"
              :loading="resetPasswordLoading"
              @click="handleResetPasswordSubmit"
            >
              确认重置
            </ElButton>
          </div>
        </template>
      </ElDialog>
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
