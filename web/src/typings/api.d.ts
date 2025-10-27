import { b } from 'vite/dist/node/moduleRunnerTransport.d-CXw_Ws6P';

/**
 * Namespace Api
 *
 * All backend api type
 */
declare namespace Api {
  namespace Common {
    /** common params of paginating */
    interface PaginatingCommonParams {
      /** current page number */
      current: number;
      /** page size */
      size: number;
      /** total count */
      total: number;
    }

    /** common params of paginating query list data */
    interface PaginatingQueryRecord<T = any> extends PaginatingCommonParams {
      records: T[];
    }

    /** common search params of table */
    type CommonSearchParams = Pick<Common.PaginatingCommonParams, 'current' | 'size'>;

    /**
     * enable status
     *
     * - "1": enabled
     * - "2": disabled
     */
    type EnableStatus = '1' | '2';

    /** common record */
    type CommonRecord<T = any> = {
      /** record id */
      id: number;
      /** record creator */
      createBy: string;
      /** record create time */
      createTime: string;
      /** record updater */
      updateBy: string;
      /** record update time */
      updateTime: string;
      /** record status */
      status: EnableStatus | undefined;
    } & T;
  }

  /**
   * namespace Auth
   *
   * backend api module: "auth"
   */
  namespace Auth {
    interface LoginToken {
      access_token: string;
      refresh_token: string;
      expires_in: number;
    }

    interface UserInfo {
      userId: string;
      userName: string;
      roles: string[];
    }
  }

  /**
   * namespace Route
   *
   * backend api module: "route"
   */
  namespace Route {
    type ElegantConstRoute = import('@elegant-router/types').ElegantConstRoute;

    interface MenuRoute extends ElegantConstRoute {
      id: string;
    }

    interface UserRoute {
      routes: MenuRoute[];
      home: import('@elegant-router/types').LastLevelRouteKey;
    }
  }

  /**
   * namespace SystemManage
   *
   * backend api module: "systemManage"
   */
  namespace SystemManage {
    type CommonSearchParams = Pick<Common.PaginatingCommonParams, 'current' | 'size'>;

    /** role */
    type Role = Common.CommonRecord<{
      /** role name */
      roleName: string;
      /** role code */
      roleCode: string;
      /** role description */
      roleDesc: string;
    }>;

    /** role search params */
    type RoleSearchParams = CommonType.RecordNullable<
      Pick<Api.SystemManage.Role, 'roleName' | 'roleCode' | 'status'> & CommonSearchParams
    >;

    /** role list */
    type RoleList = Common.PaginatingQueryRecord<Role>;

    /** all role */
    type AllRole = Pick<Role, 'id' | 'roleName' | 'roleCode'>;

    /**
     * user gender
     *
     * - "1": "male"
     * - "2": "female"
     */
    type UserGender = '1' | '2';

    /** user - 修改为匹配后端实际返回的字段 */
    type User = {
      /** user id */
      id: number;
      /** user name */
      username: string;
      /** user email */
      email: string;
      /** user full name */
      full_name?: string; // 确保包含 full_name 字段
      /** user phone */
      phone?: string;
      /** user active status */
      is_active: boolean;
      /** user admin status */
      is_admin: boolean;
      /** create time */
      created_at?: string;
      /** update time */
      updated_at?: string;
    };

    /** user search params - 修改为分字段搜索参数 */
    type UserSearchParams = CommonType.RecordNullable<{
      /** current page number */
      current: number;
      /** page size */
      size: number;
      /** username search */
      username?: string;
      /** full name search */
      full_name?: string;
      /** phone search */
      phone?: string;
      /** email search */
      email?: string;
      /** user active status filter */
      is_active?: boolean;
      /** admin status filter */
      is_admin?: boolean;
    }>;


    /** user list */
    type UserList = Common.PaginatingQueryRecord<User>;



    /**
     * menu type
     *
     * - "1": directory
     * - "2": menu
     */
    type MenuType = '1' | '2';

    type MenuButton = {
      /**
       * button code
       *
       * it can be used to control the button permission
       */
      code: string;
      /** button description */
      desc: string;
    };

    /**
     * icon type
     *
     * - "1": iconify icon
     * - "2": local icon
     */
    type IconType = '1' | '2';

    type MenuPropsOfRoute = Pick<
      import('vue-router').RouteMeta,
      | 'i18nKey'
      | 'keepAlive'
      | 'constant'
      | 'order'
      | 'href'
      | 'hideInMenu'
      | 'activeMenu'
      | 'multiTab'
      | 'fixedIndexInTab'
      | 'query'
    >;

    type Menu = Common.CommonRecord<{
      /** parent menu id */
      parentId: number;
      /** menu type */
      menuType: MenuType;
      /** menu name */
      menuName: string;
      /** route name */
      routeName: string;
      /** route path */
      routePath: string;
      /** component */
      component?: string;
      /** iconify icon name or local icon name */
      icon: string;
      /** icon type */
      iconType: IconType;
      /** buttons */
      buttons?: MenuButton[] | null;
      /** children menu */
      children?: Menu[] | null;
    }> &
      MenuPropsOfRoute;

    /** menu list */
    type MenuList = Common.PaginatingQueryRecord<Menu>;

    type MenuTree = {
      id: number;
      label: string;
      pId: number;
      children?: MenuTree[];
    };

    /** 图书管理 */
    type Book = Common.CommonRecord<{
      /** 书名 */
      title: string;
      /** 作者 */
      author: string;
      /** ISBN */
      isbn: string;
      /** 出版社 */
      publisher: string;
      /** 出版日期 */
      publish_date: string;
      /** 分类 */
      category: string;
      /** 价格 */
      price: number | undefined;
      /** 库存数量 */
      stock_quantity: number | undefined;
      /** 描述 */
      description?: string;
    }>;
    /** 图书管理 - 搜索参数 */
    type BookSearchParams = CommonType.RecordNullable<{
      /** 当前页码 */
      current: number;
      /** 每页数量 */
      size: number;
      /** 书名搜索 */
      title?: string;
      /** 作者搜索 */
      author?: string;
      /** 出版社搜索 */
      publisher?: string;
      /** ISBN 搜索 */
      isbn?: string;
      /** 分类搜索 */
      category?: string;
    }>;

    /** 图书列表 */
    type BookList = Common.PaginatingQueryRecord<Book>;

    /**
     * 借阅状态
     * - "borrowed": 借阅中
     * - "returned": 已归还
     * - "overdue": 逾期
     * - "renewed": 已续借
     */
    type BorrowStatus = 'borrowed' | 'returned' | 'overdue' | 'renewed';

    /** 借阅记录 */
    type Borrow = Common.CommonRecord<{
      /** 借阅记录ID */
      id: number;
      /** 用户ID */
      user_id: number;
      /** 图书ID */
      book_id: number;
      /** 借阅日期 */
      borrow_date: string;
      /** 到期日期 */
      due_date: string;
      /** 归还日期 */
      return_date?: string;
      /** 借阅状态 */
      status: BorrowStatus;
      /** 续借次数 */
      renewal_count: number;
      /** 罚金金额 */
      fine_amount: number;
      /** 备注 */
      notes?: string;
      /** 创建时间 */
      created_at?: string;
      /** 更新时间 */
      updated_at?: string;
    }>;

    /** 借阅记录详情（包含用户和图书信息） */
    type BorrowWithDetails = Common.CommonRecord<{
      /** 借阅记录ID */
      id: number;
      /** 用户ID */
      user_id: number;
      /** 用户名 */
      user_name: string;
      /** 用户邮箱 */
      user_email: string;
      /** 图书ID */
      book_id: number;
      /** 图书标题 */
      book_title: string;
      /** 图书作者 */
      book_author: string;
      /** 图书ISBN */
      book_isbn: string;
      /** 借阅日期 */
      borrow_date: string;
      /** 到期日期 */
      due_date: string;
      /** 归还日期 */
      return_date?: string;
      /** 借阅状态 */
      status: BorrowStatus;
      /** 续借次数 */
      renewal_count: number;
      /** 罚金金额 */
      fine_amount: number;
      /** 备注 */
      notes?: string;
      /** 逾期天数 */
      days_overdue?: number;
    }>;

    /** 借阅记录搜索参数 */
    type BorrowSearchParams = CommonType.RecordNullable<{
      /** 当前页码 */
      current: number;
      /** 每页数量 */
      size: number;
      /** 用户名 */
      username?: string;
      /** 图书名 */
      book_title?: string;
      /** 借阅状态 */
      status?: BorrowStatus;
      /** 只显示逾期记录 */
      overdue_only?: boolean;
    }>;

    /** 借阅记录列表 */
    type BorrowList = Common.PaginatingQueryRecord<BorrowWithDetails>;

    /** 借书请求参数 */
    type BorrowCreateParams = {
      /** 用户ID */
      user_id?: number;
      /** 图书ID */
      book_id: number;
      /** 借阅天数 */
      borrow_days?: number;
      /** 备注 */
      notes?: string;
    };

    /** 还书请求参数 */
    type BorrowReturnParams = {
      /** 备注 */
      notes?: string;
    };

    /** 续借请求参数 */
    type BorrowRenewalParams = {
      /** 续借天数 */
      renewal_days?: number;
      /** 备注 */
      notes?: string;
    };

    /** 借阅统计信息 */
    type BorrowStats = {
      /** 当前借阅中的图书数量 */
      current_borrows: number;
      /** 逾期图书数量 */
      overdue_borrows: number;
      /** 今日借阅数量 */
      today_borrows: number;
      /** 今日归还数量 */
      today_returns: number;
      /** 总罚金 */
      total_fines: number;
    };

    /** 逾期借阅记录 */
    type OverdueBorrow = {
      /** 借阅记录ID */
      id: number;
      /** 用户ID */
      user_id: number;
      /** 用户名 */
      username: string;
      /** 用户邮箱 */
      email: string;
      /** 用户电话 */
      phone?: string;
      /** 图书ID */
      book_id: number;
      /** 图书标题 */
      book_title: string;
      /** 图书作者 */
      book_author: string;
      /** 借阅日期 */
      borrow_date: string;
      /** 到期日期 */
      due_date: string;
      /** 续借次数 */
      renewal_count: number;
      /** 逾期天数 */
      days_overdue: number;
    };

    type UserSummary = {
      total_borrows: number;
      active_borrows: number;
      overdue_borrows: number;
    }
    type Statistics = {
      total_users: number;
      total_books: number;
      total_borrows: number;
      active_borrows: number;
      overdue_borrows: number;
  }

}
