import { request } from '../request';

/**
 * Login
 *
 * @param userName User name
 * @param password Password
 */
export function fetchLogin(userName: string, password: string) {
  return request<Api.Auth.LoginToken>({
    url: '/auth/login',
    method: 'post',
    data: {
      userName,
      password
    }
  });
}

/** Get user info */
export function fetchGetUserInfo() {
  return request<Api.Auth.UserInfo>({ url: '/auth/getUserInfo' });
}

/**
 * Refresh token
 *
 * @param refreshToken Refresh token
 */
export function fetchRefreshToken(refreshToken: string) {
  return request<Api.Auth.LoginToken>({
    url: '/auth/refreshToken',
    method: 'post',
    data: {
      refreshToken
    }
  });
}

/**
 * return custom backend error
 *
 * @param code error code
 * @param msg error message
 */
export function fetchCustomBackendError(code: string, msg: string) {
  return request({ url: '/auth/error', params: { code, msg } });
}

export function fetchUpdateUserInfo(userInfo: Api.SystemManage.User) {
  return request({
    url: '/users',
    method: 'put',
    data: userInfo
  });
}

export function fetchUpdatePassword(passwordData: {
  old_password: string;
  new_password: string;
}) {
  return request({
    url: '/users/change-password',
    method: 'patch',
    data: passwordData
  });
}

export function fetchLogout() {
  return request({ url: '/auth/logout', method: 'post' });
}

export function fetchRegister(userData: {
  username: string;
  email: string;
  full_name: string;
  password: string;
  phone?: string;
}) {
  return request({
    url: '/auth/register',
    method: 'post',
    data: userData
  });
}

export function fetchUserSummary() {
  return request<Api.SystemManage.UserSummary>({ url: '/users/stats/summary' });
}
export function fetchStatistics() {
  return request<Api.SystemManage.Statistics>({ url: '/statistics' });
}
