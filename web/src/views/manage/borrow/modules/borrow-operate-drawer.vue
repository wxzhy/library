<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue';
import { useForm, useFormRules } from '@/hooks/common/form';
import { $t } from '@/locales';
import {
  fetchBorrowBook,
  fetchGetBorrowDetail,
  fetchGetUserList,
  fetchGetBookList
} from '@/service/api';

defineOptions({ name: 'BorrowOperateDrawer' });

interface Props {
  /** the type of operation */
  operateType: UI.TableOperateType;
  /** the edit row data */
  rowData?: any | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
  default: false
});

const { formRef, validate, restoreValidation } = useForm();
const { defaultRequiredRule } = useFormRules();

// 添加加载状态
const loading = ref(false);

const title = computed(() => {
  const titles: Record<UI.TableOperateType, string> = {
    add: '办理借书',
    edit: '借阅详情'
  };
  return titles[props.operateType];
});

interface BorrowModel {
  user_id: number | undefined;
  book_id: number | undefined;
  borrow_days: number;
  notes: string;
}

interface BorrowDetail {
  id: number;
  user_name: string;
  user_email: string;
  book_title: string;
  book_author: string;
  book_isbn: string;
  borrow_date: string;
  due_date: string;
  return_date?: string;
  status: string;
  renewal_count: number;
  fine_amount: number;
  notes?: string;
  days_overdue?: number;
}

const model = ref(createDefaultModel());
const detail = ref<BorrowDetail | null>(null);
const users = ref<any[]>([]);
const books = ref<any[]>([]);
const usersLoading = ref(false);
const booksLoading = ref(false);

function createDefaultModel(): BorrowModel {
  return {
    user_id: undefined,
    book_id: undefined,
    borrow_days: 30,
    notes: ''
  };
}

const rules: Record<string, App.Global.FormRule> = {
  user_id: defaultRequiredRule,
  book_id: defaultRequiredRule,
  borrow_days: defaultRequiredRule
};

async function loadUsers(query?: string) {
  if (usersLoading.value) return;
  usersLoading.value = true;
  try {
    const response = await fetchGetUserList({
      current: 1,
      size: 50,
      search: query
    });
    users.value = response.records || [];
  } catch (error) {
    console.error('Failed to load users:', error);
    window.$message?.error('加载用户列表失败');
  } finally {
    usersLoading.value = false;
  }
}

async function loadBooks(query?: string) {
  if (booksLoading.value) return;
  booksLoading.value = true;
  try {
    const response = await fetchGetBookList({
      current: 1,
      size: 50,
      title: query
    });
    books.value = response.records || [];
  } catch (error) {
    console.error('Failed to load books:', error);
    window.$message?.error('加载图书列表失败');
  } finally {
    booksLoading.value = false;
  }
}

async function loadBorrowDetail() {
  if (props.operateType === 'edit' && props.rowData?.id) {
    loading.value = true;
    try {
      const response = await fetchGetBorrowDetail(props.rowData.id);
      detail.value = response;
    } catch (error) {
      console.error('Failed to load borrow detail:', error);
      window.$message?.error('加载借阅详情失败');
    } finally {
      loading.value = false;
    }
  }
}

async function handleInitModel() {
  model.value = createDefaultModel();
  detail.value = null;
  loading.value = false;

  if (props.operateType === 'edit') {
    await loadBorrowDetail();
  } else if (props.operateType === 'add') {
    // 预加载用户和图书数据
    await Promise.all([
      loadUsers(),
      loadBooks()
    ]);
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  if (props.operateType === 'edit') {
    closeDrawer();
    return;
  }

  await validate();

  try {
    loading.value = true;
    await fetchBorrowBook(model.value);
    window.$message?.success('借书成功');
    closeDrawer();
    emit('submitted');
  } catch (error) {
    window.$message?.error(`借书失败: ${error.message || error}`);
  } finally {
    loading.value = false;
  }
}

const statusText = computed(() => {
  const statusMap = {
    borrowed: '借阅中',
    returned: '已归还',
    overdue: '逾期',
    renewed: '已续借'
  };
  return statusMap[detail.value?.status] || '未知';
});

const statusType = computed(() => {
  const statusMap = {
    borrowed: 'primary',
    returned: 'success',
    overdue: 'danger',
    renewed: 'warning'
  };
  return statusMap[detail.value?.status] || 'info';
});

watch(visible, async (newVisible) => {
  if (newVisible) {
    await handleInitModel();
    restoreValidation();
  }
});
</script>

<template>
  <ElDrawer v-model="visible" :title="title" :size="480">
    <!-- 全局加载状态 -->
    <div v-if="loading" class="flex justify-center py-8">
      <ElEmpty description="加载中...">
        <template #image>
          <ElIcon class="animate-spin text-24px">
            <icon-mdi-loading />
          </ElIcon>
        </template>
      </ElEmpty>
    </div>

    <!-- 借书表单 -->
    <ElForm
      v-else-if="operateType === 'add'"
      ref="formRef"
      :model="model"
      :rules="rules"
      label-position="top"
    >
      <ElFormItem label="选择用户" prop="user_id">
        <ElSelect
          v-model="model.user_id"
          placeholder="请选择或搜索用户"
          filterable
          remote
          clearable
          reserve-keyword
          :remote-method="loadUsers"
          :loading="usersLoading"
          style="width: 100%"
        >
          <ElOption
            v-for="user in users"
            :key="user.id"
            :label="`${user.username} (${user.email})`"
            :value="user.id"
          />
        </ElSelect>
      </ElFormItem>

      <ElFormItem label="选择图书" prop="book_id">
        <ElSelect
          v-model="model.book_id"
          placeholder="请选择或搜索图书"
          filterable
          remote
          clearable
          reserve-keyword
          :remote-method="loadBooks"
          :loading="booksLoading"
          style="width: 100%"
        >
          <ElOption
            v-for="book in books"
            :key="book.id"
            :label="`${book.title} - ${book.author}`"
            :value="book.id"
          >
            <div>
              <div>{{ book.title }}</div>
              <div class="text-xs text-gray-500">{{ book.author }} · 库存: {{ book.stock_quantity }}</div>
            </div>
          </ElOption>
        </ElSelect>
      </ElFormItem>

      <ElFormItem label="借阅天数" prop="borrow_days">
        <ElInputNumber
          v-model="model.borrow_days"
          :min="1"
          :max="365"
          placeholder="请输入借阅天数"
          style="width: 100%"
        />
      </ElFormItem>

      <ElFormItem label="备注" prop="notes">
        <ElInput
          v-model="model.notes"
          type="textarea"
          :rows="3"
          placeholder="请输入备注信息"
        />
      </ElFormItem>
    </ElForm>

    <!-- 借阅详情 -->
    <div v-else-if="operateType === 'edit' && detail" class="space-y-4">
      <ElDescriptions title="借阅信息" :column="1" border>
        <ElDescriptionsItem label="借阅ID">{{ detail.id }}</ElDescriptionsItem>
        <ElDescriptionsItem label="用户信息">
          <div>
            <div>{{ detail.user_name }}</div>
            <div class="text-xs text-gray-500">{{ detail.user_email }}</div>
          </div>
        </ElDescriptionsItem>
        <ElDescriptionsItem label="图书信息">
          <div>
            <div class="font-medium">{{ detail.book_title }}</div>
            <div class="text-xs text-gray-500">{{ detail.book_author }} · {{ detail.book_isbn }}</div>
          </div>
        </ElDescriptionsItem>
        <ElDescriptionsItem label="借阅日期">
          {{ new Date(detail.borrow_date).toLocaleString() }}
        </ElDescriptionsItem>
        <ElDescriptionsItem label="到期日期">
          {{ new Date(detail.due_date).toLocaleString() }}
        </ElDescriptionsItem>
        <ElDescriptionsItem label="归还日期">
          {{ detail.return_date ? new Date(detail.return_date).toLocaleString() : '未归还' }}
        </ElDescriptionsItem>
        <ElDescriptionsItem label="借阅状态">
          <ElTag :type="statusType">{{ statusText }}</ElTag>
        </ElDescriptionsItem>
        <ElDescriptionsItem label="续借次数">{{ detail.renewal_count }}</ElDescriptionsItem>
        <ElDescriptionsItem label="罚金金额">
          {{ detail.fine_amount > 0 ? `¥${detail.fine_amount}` : '无' }}
        </ElDescriptionsItem>
        <ElDescriptionsItem v-if="detail.days_overdue > 0" label="逾期天数">
          <ElTag type="danger">{{ detail.days_overdue }}天</ElTag>
        </ElDescriptionsItem>
        <ElDescriptionsItem v-if="detail.notes" label="备注">{{ detail.notes }}</ElDescriptionsItem>
      </ElDescriptions>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="operateType === 'edit'" class="flex justify-center py-8">
      <ElEmpty description="加载失败，请重试">
        <ElButton type="primary" @click="handleInitModel">重新加载</ElButton>
      </ElEmpty>
    </div>

    <template #footer>
      <ElSpace :size="16">
        <ElButton @click="closeDrawer" :disabled="loading">
          {{ operateType === 'edit' ? '关闭' : $t('common.cancel') }}
        </ElButton>
        <ElButton
          v-if="operateType === 'add'"
          type="primary"
          @click="handleSubmit"
          :loading="loading"
        >
          {{ $t('common.confirm') }}
        </ElButton>
      </ElSpace>
    </template>
  </ElDrawer>
</template>

<style scoped></style>
