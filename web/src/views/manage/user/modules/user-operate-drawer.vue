<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { fetchCreateUser, fetchUpdateUser } from '@/service/api';
import { useForm, useFormRules } from '@/hooks/common/form';
import { $t } from '@/locales';


defineOptions({ name: 'UserOperateDrawer' });

interface Props {
  /** the type of operation */
  operateType: UI.TableOperateType;
  /** the edit row data */
  rowData?: Api.SystemManage.User | null;
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

const title = computed(() => {
  const titles: Record<UI.TableOperateType, string> = {
    add: $t('page.manage.user.addUser'),
    edit: $t('page.manage.user.editUser')
  };
  return titles[props.operateType];
});

// 修改模型类型，包含 full_name
type Model = Pick<
  Api.SystemManage.User,
  'username' | 'email' | 'full_name' | 'phone' | 'is_active' | 'is_admin'
> & {
  password?: string; // 新增用户时需要密码
};

const model = ref(createDefaultModel());

function createDefaultModel(): Model {
  return {
    username: '',
    email: '',
    full_name: '', // 添加 full_name 字段
    phone: null,
    is_active: true,
    is_admin: false,
    password: '' // 仅新增时使用
  };
}

// 修改验证规则，包含 full_name
type RuleKey = Extract<keyof Model, 'username' | 'email' | 'full_name' | 'password'>;

const rules = computed<Record<RuleKey, App.Global.FormRule>>(() => {
  const baseRules: Record<RuleKey, App.Global.FormRule> = {
    username: [
      { required: true, message: '请输入用户名' },
      { min: 3, max: 20, message: '用户名长度为3-20个字符' }
    ],
    email: [
      { required: true, message: '请输入邮箱' },
      { type: 'email', message: '请输入正确的邮箱格式' }
    ],
    full_name: [
      { required: true, message: '请输入姓名' },
      { max: 50, message: '姓名不能超过50个字符' }
    ],
    password: props.operateType === 'add'
      ? [
        { required: true, message: '请输入密码' },
        { min: 6, message: '密码不能少于6位' }
      ]
      : []
  };

  return baseRules;
});

// 用户状态选项
const statusOptions = [
  { label: '启用', value: true },
  { label: '禁用', value: false }
];

// 管理员状态选项
const adminOptions = [
  { label: '是', value: true },
  { label: '否', value: false }
];

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    model.value = {
      username: props.rowData.username,
      email: props.rowData.email,
      full_name: props.rowData.full_name, // 添加 full_name 映射
      phone: props.rowData.phone,
      is_active: props.rowData.is_active,
      is_admin: props.rowData.is_admin
    };
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  // 准备提交数据，包含 full_name
  const submitData = {
    username: model.value.username,
    email: model.value.email,
    full_name: model.value.full_name, // 添加 full_name
    phone: model.value.phone || null,
    is_active: model.value.is_active,
    is_admin: model.value.is_admin
  };

  // 如果是新增，包含密码
  if (props.operateType === 'add') {
    Object.assign(submitData, { password: model.value.password });
  }

  try {
    // 这里应该调用相应的 API
    if (props.operateType === 'add') {
      await fetchCreateUser(submitData);
      console.log('创建用户:', submitData);
    } else {
      await fetchUpdateUser(props.rowData!.id, submitData);
      console.log('更新用户:', submitData);
    }

    window.$message?.success(
      props.operateType === 'add'
        ? $t('common.addSuccess')
        : $t('common.updateSuccess')
    );
    closeDrawer();
    emit('submitted');
  } catch (error) {
    window.$message?.error('操作失败');
  }
}

watch(visible, () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
  }
});
</script>

<template>
  <ElDrawer v-model="visible" :title="title" :size="360">
    <ElForm ref="formRef" :model="model" :rules="rules" label-position="top">
      <!-- 用户名 -->
      <ElFormItem label="用户名" prop="username">
        <ElInput v-model="model.username" placeholder="请输入用户名" :disabled="props.operateType === 'edit'" />
      </ElFormItem>

      <!-- 姓名 -->
      <ElFormItem label="姓名" prop="full_name">
        <ElInput v-model="model.full_name" placeholder="请输入姓名" />
      </ElFormItem>

      <!-- 邮箱 -->
      <ElFormItem label="邮箱" prop="email">
        <ElInput v-model="model.email" placeholder="请输入邮箱" type="email" />
      </ElFormItem>

      <!-- 密码（仅新增时显示） -->
      <ElFormItem v-if="props.operateType === 'add'" label="密码" prop="password">
        <ElInput v-model="model.password" placeholder="请输入密码" type="password" show-password />
      </ElFormItem>

      <!-- 手机号 -->
      <ElFormItem label="手机号" prop="phone">
        <ElInput v-model="model.phone" placeholder="请输入手机号（可选）" />
      </ElFormItem>

      <!-- 用户状态 -->
      <ElFormItem label="用户状态" prop="is_active">
        <ElRadioGroup v-model="model.is_active">
          <ElRadio v-for="item in statusOptions" :key="String(item.value)" :value="item.value">
            {{ item.label }}
          </ElRadio>
        </ElRadioGroup>
      </ElFormItem>

      <!-- 管理员权限 -->
      <ElFormItem label="管理员权限" prop="is_admin">
        <ElRadioGroup v-model="model.is_admin">
          <ElRadio v-for="item in adminOptions" :key="String(item.value)" :value="item.value">
            {{ item.label }}
          </ElRadio>
        </ElRadioGroup>
      </ElFormItem>
    </ElForm>

    <template #footer>
      <ElSpace :size="16">
        <ElButton @click="closeDrawer">{{ $t('common.cancel') }}</ElButton>
        <ElButton type="primary" @click="handleSubmit">{{ $t('common.confirm') }}</ElButton>
      </ElSpace>
    </template>
  </ElDrawer>
</template>

<style scoped></style>
