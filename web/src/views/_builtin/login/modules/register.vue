<script setup lang="ts">
import { computed, ref } from 'vue';
import { $t } from '@/locales';
import { useRouterPush } from '@/hooks/common/router';
import { useForm, useFormRules } from '@/hooks/common/form';
import { fetchRegister } from '@/service/api';

defineOptions({ name: 'Register' });

const { toggleLoginModule } = useRouterPush();
const { formRef, validate } = useForm();
const registerLoading = ref(false);

interface FormModel {
  userName: string;
  realName: string;
  email: string;
  phone: string;
  password: string;
  confirmPassword: string;
}

const model = ref<FormModel>({
  userName: '',
  realName: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: ''
});

const rules = computed<Record<keyof FormModel, App.Global.FormRule[]>>(() => {
  const { formRules, createConfirmPwdRule } = useFormRules();

  return {
    userName: formRules.userName,
    realName: [
      { required: true, message: '请输入真实姓名', trigger: 'blur' },
      { min: 2, max: 20, message: '真实姓名长度应为2-20个字符', trigger: 'blur' }
    ],
    email: formRules.email,
    phone: formRules.phone,
    password: formRules.pwd,
    confirmPassword: createConfirmPwdRule(model.value.password)
  };
});

async function handleSubmit() {
  await validate();

  registerLoading.value = true;

  try {
    // 根据API接口字段定义映射数据
    const registerData = {
      username: model.value.userName, // API期望 username
      full_name: model.value.realName, // API期望 full_name
      email: model.value.email,
      password: model.value.password,
      phone: model.value.phone || undefined  // phone是可选的
    };

    await fetchRegister(registerData);

    window.$message?.success('注册成功！请使用用户名和密码登录');

    // 注册成功后跳转到登录页面
    toggleLoginModule('pwd-login');

  } catch (error) {
    console.error('注册失败:', error);
    window.$message?.error(error?.message || '注册失败，请稍后重试');
  } finally {
    registerLoading.value = false;
  }
}
</script>

<template>
  <ElForm ref="formRef" :model="model" :rules="rules" size="large" :show-label="false" @keyup.enter="handleSubmit">
    <ElFormItem prop="userName">
      <ElInput v-model="model.userName" :placeholder="$t('page.login.common.userNamePlaceholder')" />
    </ElFormItem>
    <ElFormItem prop="realName">
      <ElInput v-model="model.realName" placeholder="请输入真实姓名" />
    </ElFormItem>
    <ElFormItem prop="email">
      <ElInput v-model="model.email" type="email" placeholder="请输入邮箱地址" />
    </ElFormItem>
    <ElFormItem prop="phone">
      <ElInput v-model="model.phone" :placeholder="$t('page.login.common.phonePlaceholder')" />
    </ElFormItem>
    <ElFormItem prop="password">
      <ElInput
        v-model="model.password"
        type="password"
        show-password-on="click"
        :placeholder="$t('page.login.common.passwordPlaceholder')"
      />
    </ElFormItem>
    <ElFormItem prop="confirmPassword">
      <ElInput
        v-model="model.confirmPassword"
        type="password"
        show-password-on="click"
        :placeholder="$t('page.login.common.confirmPasswordPlaceholder')"
      />
    </ElFormItem>
    <ElSpace direction="vertical" :size="18" fill class="w-full">
      <ElButton
        type="primary"
        size="large"
        round
        block
        :loading="registerLoading"
        @click="handleSubmit"
      >
        {{ registerLoading ? '注册中...' : $t('common.confirm') }}
      </ElButton>
      <ElButton size="large" round @click="toggleLoginModule('pwd-login')">
        {{ $t('page.login.common.back') }}
      </ElButton>
    </ElSpace>
  </ElForm>
</template>

<style scoped></style>
