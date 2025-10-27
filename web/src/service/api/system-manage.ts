import { request } from '../request';

/** get role list */
export function fetchGetRoleList(params?: Api.SystemManage.RoleSearchParams) {
  return request<Api.SystemManage.RoleList>({
    url: '/systemManage/getRoleList',
    method: 'get',
    params
  });
}

/**
 * get all roles
 *
 * these roles are all enabled
 */
export function fetchGetAllRoles() {
  return request<Api.SystemManage.AllRole[]>({
    url: '/systemManage/getAllRoles',
    method: 'get'
  });
}

/** get user list */
export function fetchGetUserList(params?: Api.SystemManage.UserSearchParams) {
  return request<Api.SystemManage.UserList>({
    url: '/users',
    method: 'get',
    params
  });
}

/** get menu list */
export function fetchGetMenuList() {
  return request<Api.SystemManage.MenuList>({
    url: '/systemManage/getMenuList/v2',
    method: 'get'
  });
}

/** get all pages */
export function fetchGetAllPages() {
  return request<string[]>({
    url: '/systemManage/getAllPages',
    method: 'get'
  });
}

/** get menu tree */
export function fetchGetMenuTree() {
  return request<Api.SystemManage.MenuTree[]>({
    url: '/systemManage/getMenuTree',
    method: 'get'
  });
}

/** delete user list */
export function fetchDeleteUserList(userIds: number[]) {
  return request({
    url: '/users',
    method: 'delete',
    data: userIds
  });
}

/** delete user */
export function fetchDeleteUser(userId: number) {
  return request({
    url: `/users/${userId}`,
    method: 'delete'
  });
}

// 获取用户详情
export function fetchGetUserDetail(userId: number) {
  return request<Api.SystemManage.User>({
    url: `/users/${userId}`,
    method: 'get'
  });
}

// 更新用户信息
export function fetchUpdateUser(userId: number, userData: Api.SystemManage.User) {
  return request({
    url: `/users/${userId}`,
    method: 'put',
    data: userData
  });
}

// 修改密码
export function resetUserPassword(userId: number, newPassword: string) {
  return request({
    url: `/users/${userId}/reset-password`,
    method: 'patch',
    data: { new_password: newPassword }
  });
}

// 创建新用户
export function fetchCreateUser(userData: {
  username: string;
  fullName: string;
  email: string;
  phone?: string;
  password: string;
  roles: number[]; // 角色ID数组
}) {
  return request({
    url: '/users',
    method: 'post',
    data: userData
  });
}

// 批量删除用户
export function fetchBatchDeleteUsers(userIds: number[]) {
  return request({
    url: '/users/batch-delete',
    method: 'post',
    data: { user_ids: userIds }
  });
}

export function fetchGetBookList(params?: Api.SystemManage.BookSearchParams) {
  return request<Api.SystemManage.BookList>({
    url: '/books',
    method: 'get',
    params
  });
}

export function fetchGetBookDetail(bookId: number) {
  return request<Api.SystemManage.Book>({
    url: `/books/${bookId}`,
    method: 'get'
  });
}
export function fetchCreateBook(bookData: Api.SystemManage.Book) {
  return request({
    url: '/books',
    method: 'post',
    data: bookData
  });
}

export function fetchUpdateBook(bookId: number, bookData: Api.SystemManage.Book) {
  // bookData should contain all necessary fields to update the book
  return request({
    url: `/books/${bookId}`,
    method: 'put',
    data: bookData
  });
}

export function fetchDeleteBook(bookId: number) {
  return request({
    url: `/books/${bookId}`,
    method: 'delete'
  });
}

export function fetchDeleteBookList(bookIds: number[]) {
  return request({
    url: '/books',
    method: 'delete',
    data: bookIds
  });
}

export function fetchGetCategoryList() {
  return request<{categories: string[]}>({
    url: '/books/categories/list',
    method: 'get'
  });
}

export function fetchGetAuthorList() {
  return request<{authors: string[]}>({
    url: '/books/authors/list',
    method: 'get'
  });
}

export function fetchBatchDeleteBooks(bookIds: number[]) {
  return request({
    url: '/books/batch-delete',
    method: 'post',
    data: { book_ids: bookIds }
  });
}
// ============== 借阅管理相关API ==============

/** 获取借阅记录列表 */
export function fetchGetBorrowList(params?: Api.SystemManage.BorrowSearchParams) {
  return request<Api.SystemManage.BorrowList>({
    url: '/borrows',
    method: 'get',
    params: {
      ...params,
      page: params?.current,
      page_size: params?.size
    }
  });
}

/** 获取借阅记录详情 */
export function fetchGetBorrowDetail(borrowId: number) {
  return request<Api.SystemManage.BorrowWithDetails>({
    url: `/borrows/${borrowId}`,
    method: 'get'
  });
}

/** 借书 */
export function fetchBorrowBook(borrowData: Api.SystemManage.BorrowCreateParams) {
  return request({
    url: '/borrows/borrow',
    method: 'post',
    data: borrowData
  });
}

/** 还书 */
export function fetchReturnBook(borrowId: number, returnData?: Api.SystemManage.BorrowReturnParams) {
  return request({
    url: `/borrows/${borrowId}/return`,
    method: 'post',
    data: returnData || {}
  });
}

/** 续借 */
export function fetchRenewBook(borrowId: number, renewalData?: Api.SystemManage.BorrowRenewalParams) {
  return request({
    url: `/borrows/${borrowId}/renew`,
    method: 'post',
    data: renewalData || {}
  });
}

/** 获取用户借阅记录 */
export function fetchGetUserBorrows(userId: number, status?: Api.SystemManage.BorrowStatus) {
  return request<{ borrows: Api.SystemManage.BorrowWithDetails[] }>({
    url: `/borrows/user/${userId}`,
    method: 'get',
    params: status ? { status } : undefined
  });
}

/** 获取借阅统计信息 */
export function fetchGetBorrowStats() {
  return request<Api.SystemManage.BorrowStats>({
    url: '/borrows/stats/summary',
    method: 'get'
  });
}

/** 获取逾期借阅列表 */
export function fetchGetOverdueBorrows() {
  return request<{overdue_borrows: Api.SystemManage.OverdueBorrow[]}>({
    url: '/borrows/overdue/list',
    method: 'get'
  });
}
