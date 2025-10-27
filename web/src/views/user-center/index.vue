<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useAuthStore } from '@/store/modules/auth';
import { useForm, useFormRules } from '@/hooks/common/form';
import { $t } from '@/locales';
import { fetchUpdateUserInfo, fetchUpdatePassword } from '@/service/api/auth';

defineOptions({ name: 'UserCenter' });

const authStore = useAuthStore();
const { formRef: profileFormRef, validate: validateProfile, restoreValidation: restoreProfileValidation } = useForm();
const { formRef: passwordFormRef, validate: validatePassword, restoreValidation: restorePasswordValidation } = useForm();
const { defaultRequiredRule, emailRule, phoneRule } = useFormRules();

// 当前活跃的标签页
const activeTab = ref('profile');

// 个人信息表单
const profileForm = reactive({
  username: '',
  email: '',
  phone: '',
  full_name: '',
  bio: ''
});

// 密码修改表单
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
});

// 加载状态
const profileLoading = ref(false);
const passwordLoading = ref(false);

// 表单验证规则（移除用户名验证，因为不允许修改）
const profileRules = {
  email: [defaultRequiredRule, emailRule],
  phone: phoneRule,
  full_name: defaultRequiredRule
};

// 密码验证规则
const passwordRules = {
  current_password: defaultRequiredRule,
  new_password: [
    defaultRequiredRule,
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    defaultRequiredRule,
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
};

// 获取用户角色显示文本
function getUserRoleText() {
  const userInfo = authStore.userInfo;
  if (!userInfo) return '普通用户';

  // 处理不同的角色字段格式
  let role = '';
  if (userInfo.role) {
    role = userInfo.role;
  } else if (userInfo.roles && Array.isArray(userInfo.roles) && userInfo.roles.length > 0) {
    role = userInfo.roles[0];
  }

  return role === 'admin' ? '管理员' : '普通用户';
}

// 检查是否为管理员
function isAdmin() {
  const userInfo = authStore.userInfo;
  if (!userInfo) return false;

  if (userInfo.role === 'admin') return true;
  if (userInfo.roles && Array.isArray(userInfo.roles) && userInfo.roles.includes('admin')) return true;

  return false;
}

// 获取用户信息
async function fetchUserProfile() {
  try {
    profileLoading.value = true;

    // 使用store中的用户信息
    const userInfo = authStore.userInfo;
    console.log('当前用户信息:', userInfo); // 调试日志

    if (userInfo) {
      profileForm.username = userInfo.userName || userInfo.username || '';
      profileForm.email = userInfo.email || '';
      profileForm.phone = userInfo.phone || '';
      profileForm.full_name = userInfo.full_name || userInfo.realName || '';
      profileForm.bio = userInfo.bio || userInfo.description || '';
    }
  } catch (error) {
    console.error('获取用户信息失败:', error);
    ElMessage.error('获取用户信息失败');
  } finally {
    profileLoading.value = false;
  }
}

// 更新个人信息
async function updateProfile() {
  try {
    await validateProfile();
    profileLoading.value = true;

    // 构建更新数据，确保包含所有必要字段（不包含用户名）
    const updateData = {
      id: authStore.userInfo?.userId || authStore.userInfo?.id,
      // username: profileForm.username, // 移除用户名字段，不允许修改
      email: profileForm.email,
      phone: profileForm.phone,
      full_name: profileForm.full_name,
      bio: profileForm.bio
    };

    console.log('更新用户信息:', updateData);

    // 调用更新用户信息的API
    await fetchUpdateUserInfo(updateData as Api.SystemManage.User);

    ElMessage.success('个人信息更新成功');

    // 手动更新 store 中的用户信息（不更新用户名）
    if (authStore.userInfo) {
      // authStore.userInfo.userName = profileForm.username; // 移除用户名更新
      authStore.userInfo.email = profileForm.email;
      authStore.userInfo.phone = profileForm.phone;
      authStore.userInfo.full_name = profileForm.full_name;
      authStore.userInfo.bio = profileForm.bio;
    }

    // 或者重新获取用户信息
    // await authStore.getUserInfo();

  } catch (error: any) {
    console.error('更新个人信息失败:', error);
    const errorMessage = error?.response?.data?.detail ||
                        error?.response?.data?.message ||
                        error?.message ||
                        '更新失败，请重试';
    ElMessage.error(errorMessage);
  } finally {
    profileLoading.value = false;
  }
}

// 修改密码
async function changePassword() {
  try {
    await validatePassword();
    passwordLoading.value = true;

    // 构建密码修改数据
    const passwordData = {
      old_password: passwordForm.current_password,
      new_password: passwordForm.new_password
    };

    // 调用修改密码的API
    await fetchUpdatePassword(passwordData);

    ElMessage.success('密码修改成功');

    // 清空表单
    Object.assign(passwordForm, {
      current_password: '',
      new_password: '',
      confirm_password: ''
    });
    restorePasswordValidation();

    // 询问是否重新登录
    ElMessageBox.confirm(
      '密码已修改成功，建议重新登录以确保安全。是否立即重新登录？',
      '提示',
      {
        confirmButtonText: '重新登录',
        cancelButtonText: '稍后再说',
        type: 'info'
      }
    ).then(() => {
      authStore.logout();
    }).catch(() => {
      // 用户选择稍后再说，不做处理
    });
  } catch (error: any) {
    console.error('修改密码失败:', error);
    const errorMessage = error?.response?.data?.detail ||
                        error?.response?.data?.message ||
                        error?.message ||
                        '密码修改失败，请重试';
    ElMessage.error(errorMessage);
  } finally {
    passwordLoading.value = false;
  }
}

// 重置个人信息表单
function resetProfileForm() {
  fetchUserProfile();
  restoreProfileValidation();
}

// 重置密码表单
function resetPasswordForm() {
  Object.assign(passwordForm, {
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  restorePasswordValidation();
}

onMounted(() => {
  fetchUserProfile();
});
</script>

<template>
  <div class="user-center">
    <div class="user-center-header">
      <div class="user-avatar">
        <ElAvatar :size="80" :src="authStore.userInfo?.avatar">
          <ElIcon><icon-ep-user /></ElIcon>
        </ElAvatar>
      </div>
      <div class="user-info">
        <h2>{{ authStore.userInfo?.userName || authStore.userInfo?.username || '用户' }}</h2>
        <p class="user-email">{{ authStore.userInfo?.email || '暂无邮箱' }}</p>
        <ElTag :type="isAdmin() ? 'danger' : 'primary'" size="small">
          {{ getUserRoleText() }}
        </ElTag>
      </div>
    </div>

    <ElCard class="user-center-content">
      <ElTabs v-model="activeTab" class="user-tabs">
        <!-- 个人信息 -->
        <ElTabPane label="个人信息" name="profile">
          <div class="tab-content">
            <ElForm
              ref="profileFormRef"
              :model="profileForm"
              :rules="profileRules"
              label-width="100px"
              class="profile-form"
            >
              <ElRow :gutter="24">
                <ElCol :span="12">
                  <ElFormItem label="用户名">
                    <ElInput
                      v-model="profileForm.username"
                      placeholder="用户名不可修改"
                      disabled
                      readonly
                    >
                      <template #suffix>
                        <ElTooltip content="用户名不可修改" placement="top">
                          <ElIcon class="text-gray-400"><icon-ep-lock /></ElIcon>
                        </ElTooltip>
                      </template>
                    </ElInput>
                  </ElFormItem>
                </ElCol>
                <ElCol :span="12">
                  <ElFormItem label="邮箱" prop="email">
                    <ElInput
                      v-model="profileForm.email"
                      placeholder="请输入邮箱"
                      :disabled="profileLoading"
                    />
                  </ElFormItem>
                </ElCol>
              </ElRow>

              <ElRow :gutter="24">
                <ElCol :span="12">
                  <ElFormItem label="手机号" prop="phone">
                    <ElInput
                      v-model="profileForm.phone"
                      placeholder="请输入手机号"
                      :disabled="profileLoading"
                    />
                  </ElFormItem>
                </ElCol>
                <ElCol :span="12">
                  <ElFormItem label="真实姓名" prop="full_name">
                    <ElInput
                      v-model="profileForm.full_name"
                      placeholder="请输入真实姓名"
                      :disabled="profileLoading"
                    />
                  </ElFormItem>
                </ElCol>
              </ElRow>

              <ElFormItem label="个人简介" prop="bio">
                <ElInput
                  v-model="profileForm.bio"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入个人简介"
                  :disabled="profileLoading"
                />
              </ElFormItem>

              <ElFormItem>
                <ElSpace>
                  <ElButton
                    type="primary"
                    :loading="profileLoading"
                    @click="updateProfile"
                  >
                    <template #icon>
                      <ElIcon><icon-ep-check /></ElIcon>
                    </template>
                    {{ $t('common.save') }}
                  </ElButton>
                  <ElButton @click="resetProfileForm" :disabled="profileLoading">
                    <template #icon>
                      <ElIcon><icon-ep-refresh /></ElIcon>
                    </template>
                    {{ $t('common.reset') }}
                  </ElButton>
                </ElSpace>
              </ElFormItem>
            </ElForm>
          </div>
        </ElTabPane>

        <!-- 密码修改 -->
        <ElTabPane label="密码修改" name="password">
          <div class="tab-content">
            <ElForm
              ref="passwordFormRef"
              :model="passwordForm"
              :rules="passwordRules"
              label-width="100px"
              class="password-form"
            >
              <ElFormItem label="当前密码" prop="current_password">
                <ElInput
                  v-model="passwordForm.current_password"
                  type="password"
                  placeholder="请输入当前密码"
                  show-password
                  :disabled="passwordLoading"
                />
              </ElFormItem>

              <ElFormItem label="新密码" prop="new_password">
                <ElInput
                  v-model="passwordForm.new_password"
                  type="password"
                  placeholder="请输入新密码（至少6位）"
                  show-password
                  :disabled="passwordLoading"
                />
              </ElFormItem>

              <ElFormItem label="确认密码" prop="confirm_password">
                <ElInput
                  v-model="passwordForm.confirm_password"
                  type="password"
                  placeholder="请再次输入新密码"
                  show-password
                  :disabled="passwordLoading"
                />
              </ElFormItem>

              <ElFormItem>
                <ElSpace>
                  <ElButton
                    type="primary"
                    :loading="passwordLoading"
                    @click="changePassword"
                  >
                    <template #icon>
                      <ElIcon><icon-ep-key /></ElIcon>
                    </template>
                    修改密码
                  </ElButton>
                  <ElButton @click="resetPasswordForm" :disabled="passwordLoading">
                    <template #icon>
                      <ElIcon><icon-ep-refresh /></ElIcon>
                    </template>
                    {{ $t('common.reset') }}
                  </ElButton>
                </ElSpace>
              </ElFormItem>
            </ElForm>

            <ElAlert
              title="密码安全提示"
              type="info"
              :closable="false"
              show-icon
              class="password-tip"
            >
              <template #default>
                <ul>
                  <li>密码长度至少6位</li>
                  <li>建议包含字母、数字和特殊字符</li>
                  <li>定期更换密码以确保账户安全</li>
                  <li>不要与其他网站使用相同密码</li>
                </ul>
              </template>
            </ElAlert>
          </div>
        </ElTabPane>

        <!-- 账户安全 -->
        <ElTabPane label="账户安全" name="security">
          <div class="tab-content">
            <div class="security-section">
              <h3>账户状态</h3>
              <ElDescriptions :column="2" border>
                <ElDescriptionsItem label="用户名">
                  <span class="font-medium">{{ profileForm.username }}</span>
                  <ElTag type="info" size="small" class="ml-2">不可修改</ElTag>
                </ElDescriptionsItem>
                <ElDescriptionsItem label="账户状态">
                  <ElTag :type="authStore.userInfo?.is_active !== false ? 'success' : 'danger'">
                    {{ authStore.userInfo?.is_active !== false ? '正常' : '已禁用' }}
                  </ElTag>
                </ElDescriptionsItem>
                <ElDescriptionsItem label="注册时间">
                  {{ authStore.userInfo?.created_at ? new Date(authStore.userInfo.created_at).toLocaleString() : '-' }}
                </ElDescriptionsItem>
                <ElDescriptionsItem label="最后登录">
                  {{ authStore.userInfo?.last_login ? new Date(authStore.userInfo.last_login).toLocaleString() : '-' }}
                </ElDescriptionsItem>
                <ElDescriptionsItem label="用户角色">
                  <ElTag :type="isAdmin() ? 'danger' : 'primary'">
                    {{ getUserRoleText() }}
                  </ElTag>
                </ElDescriptionsItem>
              </ElDescriptions>
            </div>

            <div class="security-section">
              <h3>安全设置</h3>
              <div class="security-items">
                <div class="security-item">
                  <div class="security-item-info">
                    <ElIcon class="security-icon"><icon-ep-lock /></ElIcon>
                    <div>
                      <h4>登录密码</h4>
                      <p>定期更换密码可以提高账户安全性</p>
                    </div>
                  </div>
                  <ElButton type="primary" plain @click="activeTab = 'password'">
                    <template #icon>
                      <ElIcon><icon-ep-edit /></ElIcon>
                    </template>
                    修改密码
                  </ElButton>
                </div>

                <div class="security-item">
                  <div class="security-item-info">
                    <ElIcon class="security-icon"><icon-ep-message /></ElIcon>
                    <div>
                      <h4>邮箱绑定</h4>
                      <p>{{ profileForm.email || '未绑定邮箱' }}</p>
                    </div>
                  </div>
                  <ElButton type="primary" plain @click="activeTab = 'profile'">
                    <template #icon>
                      <ElIcon><icon-ep-edit /></ElIcon>
                    </template>
                    {{ profileForm.email ? '修改邮箱' : '绑定邮箱' }}
                  </ElButton>
                </div>

                <div class="security-item">
                  <div class="security-item-info">
                    <ElIcon class="security-icon"><icon-ep-phone /></ElIcon>
                    <div>
                      <h4>手机绑定</h4>
                      <p>{{ profileForm.phone || '未绑定手机' }}</p>
                    </div>
                  </div>
                  <ElButton type="primary" plain @click="activeTab = 'profile'">
                    <template #icon>
                      <ElIcon><icon-ep-edit /></ElIcon>
                    </template>
                    {{ profileForm.phone ? '修改手机' : '绑定手机' }}
                  </ElButton>
                </div>
              </div>
            </div>
          </div>
        </ElTabPane>
      </ElTabs>
    </ElCard>
  </div>
</template>

<!-- 样式保持不变 -->
<style scoped>
.user-center {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.user-center-header {
  display: flex;
  align-items: center;
  padding: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  margin-bottom: 24px;
}

.user-avatar {
  margin-right: 24px;
}

.user-info h2 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.user-email {
  margin: 0 0 12px 0;
  opacity: 0.9;
  font-size: 16px;
}

.user-center-content {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-tabs {
  min-height: 500px;
}

.tab-content {
  padding: 24px;
}

.profile-form,
.password-form {
  max-width: 600px;
}

.password-tip {
  margin-top: 24px;
}

.password-tip ul {
  margin: 0;
  padding-left: 20px;
}

.password-tip li {
  margin: 4px 0;
}

.security-section {
  margin-bottom: 32px;
}

.security-section h3 {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.security-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  transition: all 0.3s;
}

.security-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.security-item-info {
  display: flex;
  align-items: center;
}

.security-icon {
  font-size: 24px;
  color: #409eff;
  margin-right: 16px;
}

.security-item-info h4 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.security-item-info p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

@media (max-width: 768px) {
  .user-center {
    padding: 16px;
  }

  .user-center-header {
    flex-direction: column;
    text-align: center;
    padding: 24px;
  }

  .user-avatar {
    margin-right: 0;
    margin-bottom: 16px;
  }

  .tab-content {
    padding: 16px;
  }

  .security-item {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .security-item-info {
    flex-direction: column;
  }

  .security-icon {
    margin-right: 0;
    margin-bottom: 8px;
  }
}
</style>
