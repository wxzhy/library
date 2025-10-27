<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { $t } from '@/locales';
import { fetchGetUserList, fetchGetBookList } from '@/service/api';

defineOptions({ name: 'BorrowSearch' });

const activeName = ref(['borrow-search']);

interface Emits {
  (e: 'reset'): void;
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.SystemManage.BorrowSearchParams>('model', { required: true });

const statusOptions = [
  { label: '借阅中', value: 'borrowed' },
  { label: '已归还', value: 'returned' },
  { label: '逾期', value: 'overdue' },
  { label: '已续借', value: 'renewed' }
];

function reset() {
  emit('reset');
}

function search() {
  emit('search');
}
</script>

<template>
  <ElCard class="card-wrapper">
    <ElCollapse v-model="activeName">
      <ElCollapseItem title="搜索条件" name="borrow-search">
        <ElForm :model="model" label-position="right" :label-width="80">
          <ElRow :gutter="24">
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="用户名" prop="username">
                <ElInput
                  v-model="model.username"
                  placeholder="请输入用户名"
                  clearable
                />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="图书名" prop="book_title">
                <ElInput
                  v-model="model.book_title"
                  placeholder="请输入图书标题"
                  clearable
                />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="状态" prop="status">
                <ElSelect v-model="model.status" placeholder="请选择状态" clearable>
                  <ElOption
                    v-for="status in statusOptions"
                    :key="status.value"
                    :label="status.label"
                    :value="status.value"
                  />
                </ElSelect>
              </ElFormItem>
            </ElCol>
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="逾期" prop="overdue_only">
                <ElSwitch v-model="model.overdue_only" />
              </ElFormItem>
            </ElCol>
            <ElCol :lg="24" :md="24" :sm="24">
              <ElSpace class="w-full justify-end" alignment="end">
                <ElButton @click="reset">
                  <template #icon>
                    <icon-ic-round-refresh class="text-icon" />
                  </template>
                  {{ $t('common.reset') }}
                </ElButton>
                <ElButton type="primary" plain @click="search">
                  <template #icon>
                    <icon-ic-round-search class="text-icon" />
                  </template>
                  {{ $t('common.search') }}
                </ElButton>
              </ElSpace>
            </ElCol>
          </ElRow>
        </ElForm>
      </ElCollapseItem>
    </ElCollapse>
  </ElCard>
</template>

<style scoped></style>
