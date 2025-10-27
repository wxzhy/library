<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/locales';
import { useForm, useFormRules } from '@/hooks/common/form';

defineOptions({ name: 'UserSearch' });

interface Emits {
  (e: 'reset'): void;
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const { formRef, validate, restoreValidation } = useForm();

const model = defineModel<Api.SystemManage.UserSearchParams>('model', { required: true });

// 修改规则类型，匹配新的搜索参数
type RuleKey = Extract<keyof Api.SystemManage.UserSearchParams, 'username' | 'full_name' | 'phone' | 'email'>;

const rules = computed<Record<RuleKey, App.Global.FormRule>>(() => {
  return {
    username: { required: false },
    full_name: { required: false },
    phone: { required: false },
    email: { required: false }
  };
});

// 用户状态选项
const userStatusOptions = [
  { label: '启用', value: true },
  { label: '禁用', value: false }
];

// 管理员状态选项
const adminStatusOptions = [
  { label: '是', value: true },
  { label: '否', value: false }
];

async function reset() {
  await restoreValidation();
  emit('reset');
}

async function search() {
  await validate();
  emit('search');
}
</script>

<template>
  <ElCard class="card-wrapper">
    <ElCollapse>
      <ElCollapseItem :title="$t('common.search')" name="user-search">
        <ElForm ref="formRef" :model="model" :rules="rules" label-position="right" :label-width="80">
          <ElRow :gutter="24">
            <!-- 用户名搜索 -->
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="用户名" prop="username">
                <ElInput
                  v-model="model.username"
                  placeholder="搜索用户名"
                  clearable
                />
              </ElFormItem>
            </ElCol>

            <!-- 姓名搜索 -->
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="姓名" prop="full_name">
                <ElInput
                  v-model="model.full_name"
                  placeholder="搜索姓名"
                  clearable
                />
              </ElFormItem>
            </ElCol>

            <!-- 手机号搜索 -->
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="手机号" prop="phone">
                <ElInput
                  v-model="model.phone"
                  placeholder="搜索手机号"
                  clearable
                />
              </ElFormItem>
            </ElCol>

            <!-- 邮箱搜索 -->
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="邮箱" prop="email">
                <ElInput
                  v-model="model.email"
                  placeholder="搜索邮箱"
                  clearable
                />
              </ElFormItem>
            </ElCol>

            <!-- 用户状态筛选 -->
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="用户状态" prop="is_active">
                <ElSelect
                  v-model="model.is_active"
                  clearable
                  placeholder="选择用户状态"
                >
                  <ElOption
                    v-for="item in userStatusOptions"
                    :key="String(item.value)"
                    :label="item.label"
                    :value="item.value"
                  />
                </ElSelect>
              </ElFormItem>
            </ElCol>

            <!-- 管理员状态筛选 -->
            <ElCol :lg="6" :md="8" :sm="12">
              <ElFormItem label="管理员" prop="is_admin">
                <ElSelect
                  v-model="model.is_admin"
                  clearable
                  placeholder="选择管理员状态"
                >
                  <ElOption
                    v-for="item in adminStatusOptions"
                    :key="String(item.value)"
                    :label="item.label"
                    :value="item.value"
                  />
                </ElSelect>
              </ElFormItem>
            </ElCol>

            <!-- 操作按钮 -->
            <ElCol :lg="24" :md="8" :sm="12">
              <ElSpace class="w-full justify-end" alignment="end">
                <ElButton @click="reset">
                  <template #icon>
                    <icon-ic-round-refresh class="text-icon" />
                  </template>
                  {{ $t('common.reset') }}
                </ElButton>
                <ElButton type="primary" @click="search">
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
