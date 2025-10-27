-- 图书管理系统数据库初始化脚本
-- 创建时间: 2024

-- 创建数据库
CREATE DATABASE IF NOT EXISTS library_management 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE library_management;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    hashed_password VARCHAR(255) NOT NULL COMMENT '加密密码',
    full_name VARCHAR(100) COMMENT '真实姓名',
    phone VARCHAR(20) COMMENT '手机号',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    is_admin BOOLEAN DEFAULT FALSE COMMENT '是否管理员',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB COMMENT='用户表';

-- 图书表
CREATE TABLE IF NOT EXISTS books (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL COMMENT '书名',
    author VARCHAR(100) NOT NULL COMMENT '作者',
    isbn VARCHAR(20) NOT NULL UNIQUE COMMENT 'ISBN编号',
    publisher VARCHAR(100) NOT NULL COMMENT '出版社',
    publish_date VARCHAR(20) NOT NULL COMMENT '出版日期',
    category VARCHAR(50) NOT NULL COMMENT '分类',
    price DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '价格',
    stock_quantity INT NOT NULL DEFAULT 0 COMMENT '库存数量',
    description TEXT COMMENT '描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB COMMENT='图书表';

-- 借阅记录表
CREATE TABLE IF NOT EXISTS borrows (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    book_id INT NOT NULL COMMENT '图书ID',
    borrow_date TIMESTAMP NOT NULL COMMENT '借阅日期',
    due_date TIMESTAMP NOT NULL COMMENT '应还日期',
    return_date TIMESTAMP NULL COMMENT '实际归还日期',
    status ENUM('borrowed', 'returned', 'overdue', 'renewed') DEFAULT 'borrowed' COMMENT '状态',
    renewal_count INT DEFAULT 0 COMMENT '续借次数',
    fine_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '罚金',
    notes TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='借阅记录表';

-- 创建索引优化查询性能
-- 用户表索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 图书表索引
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_books_isbn ON books(isbn);
CREATE INDEX idx_books_category ON books(category);
CREATE INDEX idx_books_stock_quantity ON books(stock_quantity);
CREATE INDEX idx_books_created_at ON books(created_at);

-- 借阅记录表索引
CREATE INDEX idx_borrows_user_id ON borrows(user_id);
CREATE INDEX idx_borrows_book_id ON borrows(book_id);
CREATE INDEX idx_borrows_status ON borrows(status);
CREATE INDEX idx_borrows_borrow_date ON borrows(borrow_date);
CREATE INDEX idx_borrows_due_date ON borrows(due_date);
CREATE INDEX idx_borrows_return_date ON borrows(return_date);
CREATE INDEX idx_borrows_user_status ON borrows(user_id, status);

-- 插入初始管理员用户
INSERT INTO users (username, email, hashed_password, full_name, is_admin) 
VALUES (
    'admin', 
    'admin@library.com', 
    'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', -- 密码: admin123
    '系统管理员', 
    TRUE
);

-- 插入测试用户
INSERT INTO users (username, email, hashed_password, full_name, phone) 
VALUES 
    ('user1', 'user1@test.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', '张三', '13812345678'),
    ('user2', 'user2@test.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', '李四', '13987654321'),
    ('user3', 'user3@test.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', '王五', '13655556666');

-- 插入测试图书数据
INSERT INTO books (title, author, isbn, publisher, publish_date, category, price, stock_quantity, description) 
VALUES 
    ('Python编程：从入门到实践', 'Eric Matthes', '9787115428028', '人民邮电出版社', '2016-07', '计算机', 89.00, 10, 'Python编程入门经典教程'),
    ('算法导论', 'Thomas H.Cormen', '9787111407010', '机械工业出版社', '2013-01', '计算机', 128.00, 5, '算法和数据结构的经典教材'),
    ('深入理解计算机系统', 'Randal E.Bryant', '9787111321312', '机械工业出版社', '2011-01', '计算机', 139.00, 8, '计算机系统的经典教材'),
    ('红楼梦', '曹雪芹', '9787020002207', '人民文学出版社', '1996-12', '文学', 59.70, 15, '中国古典文学四大名著之一'),
    ('三国演义', '罗贯中', '9787020002191', '人民文学出版社', '1998-05', '文学', 66.00, 12, '中国古典文学四大名著之一'),
    ('西游记', '吴承恩', '9787020002184', '人民文学出版社', '1999-02', '文学', 56.00, 18, '中国古典文学四大名著之一'),
    ('水浒传', '施耐庵', '9787020002177', '人民文学出版社', '1997-01', '文学', 68.00, 10, '中国古典文学四大名著之一'),
    ('Java核心技术', 'Cay S. Horstmann', '9787111213826', '机械工业出版社', '2007-06', '计算机', 119.00, 6, 'Java编程权威指南'),
    ('设计模式', 'Erich Gamma', '9787111075646', '机械工业出版社', '2000-09', '计算机', 35.00, 4, '软件设计模式经典教材'),
    ('简·爱', '夏洛蒂·勃朗特', '9787020024681', '人民文学出版社', '2003-05', '文学', 28.00, 20, '英国文学经典作品');

-- 插入测试借阅记录
INSERT INTO borrows (user_id, book_id, borrow_date, due_date, status, notes) 
VALUES 
    (2, 1, '2024-01-15 10:00:00', '2024-02-14 23:59:59', 'borrowed', '第一次借阅'),
    (3, 4, '2024-01-20 14:30:00', '2024-02-19 23:59:59', 'borrowed', '借阅红楼梦'),
    (2, 8, '2024-01-10 09:15:00', '2024-02-09 23:59:59', 'returned', '已归还'),
    (3, 2, '2024-01-05 16:20:00', '2024-02-04 23:59:59', 'returned', '算法学习');

-- 更新已归还图书的归还时间
UPDATE borrows SET return_date = '2024-01-25 10:30:00' WHERE id = 3;
UPDATE borrows SET return_date = '2024-01-28 15:45:00' WHERE id = 4;

-- 创建视图：用户借阅统计
CREATE VIEW user_borrow_stats AS
SELECT 
    u.id as user_id,
    u.username,
    u.full_name,
    COUNT(b.id) as total_borrows,
    COUNT(CASE WHEN b.status = 'borrowed' THEN 1 END) as current_borrows,
    COUNT(CASE WHEN b.status = 'returned' THEN 1 END) as returned_books,
    COUNT(CASE WHEN b.status = 'borrowed' AND b.due_date < NOW() THEN 1 END) as overdue_books,
    IFNULL(SUM(b.fine_amount), 0) as total_fines
FROM users u
LEFT JOIN borrows b ON u.id = b.user_id
GROUP BY u.id, u.username, u.full_name;

-- 创建视图：用户借阅详情
CREATE VIEW user_borrow_details AS
SELECT 
    u.id as user_id,
    u.username,
    u.full_name,
    b.id as borrow_id,
    b.book_id,
    bk.title as book_title,
    b.borrow_date,
    b.due_date,
    b.return_date,
    b.status,
    b.renewal_count,
    b.fine_amount,
    b.notes
FROM users u
LEFT JOIN borrows b ON u.id = b.user_id
LEFT JOIN books bk ON b.book_id = bk.id
ORDER BY u.id, b.borrow_date DESC;

-- 创建视图：所有借阅记录
CREATE VIEW all_borrow_records AS
SELECT
    b.id as borrow_id,
    u.id as user_id,
    u.username,
    bk.id as book_id,
    bk.title as book_title,
    b.borrow_date,
    b.due_date,
    b.return_date,
    b.status,
    b.renewal_count,
    b.fine_amount,
    b.notes
FROM borrows b
LEFT JOIN users u ON b.user_id = u.id
LEFT JOIN books bk ON b.book_id = bk.id
ORDER BY b.borrow_date DESC;

-- 创建视图：图书借阅统计
CREATE VIEW book_borrow_stats AS
SELECT 
    bk.id as book_id,
    bk.title,
    bk.author,
    bk.category,
    bk.stock_quantity,
    COUNT(b.id) as total_borrows,
    COUNT(CASE WHEN b.status = 'borrowed' THEN 1 END) as current_borrows,
    COUNT(CASE WHEN b.status = 'returned' THEN 1 END) as times_borrowed
FROM books bk
LEFT JOIN borrows b ON bk.id = b.book_id
GROUP BY bk.id, bk.title, bk.author, bk.category, bk.stock_quantity;

-- 创建存储过程：自动处理逾期
DELIMITER //
CREATE PROCEDURE UpdateOverdueStatus()
BEGIN
    UPDATE borrows 
    SET status = 'overdue' 
    WHERE status = 'borrowed' 
    AND due_date < NOW() 
END //
DELIMITER ;

-- 创建事件：每天自动更新逾期状态
CREATE EVENT IF NOT EXISTS UpdateOverdueEvent
ON SCHEDULE EVERY 1 DAY
DO
BEGIN
    CALL UpdateOverdueStatus();
END;


-- 创建触发器：借书时检查库存
DELIMITER //
CREATE TRIGGER check_stock_before_borrow
BEFORE INSERT ON borrows
FOR EACH ROW
BEGIN
    DECLARE current_stock INT;
    SELECT stock_quantity INTO current_stock FROM books WHERE id = NEW.book_id;
    
    IF current_stock <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '图书库存不足，无法借阅';
    END IF;
END //
DELIMITER ;

-- 创建触发器：借书时自动减少库存
DELIMITER //
CREATE TRIGGER update_stock_on_borrow
BEFORE INSERT ON borrows
FOR EACH ROW
BEGIN
    UPDATE books SET stock_quantity = stock_quantity - 1 WHERE id = NEW.book_id;
END //

-- 创建触发器：还书时自动增加库存
DELIMITER //
CREATE TRIGGER update_stock_on_return
AFTER UPDATE ON borrows
FOR EACH ROW
BEGIN
    IF OLD.status = 'borrowed' AND NEW.status = 'returned' THEN
        UPDATE books SET stock_quantity = stock_quantity + 1 WHERE id = NEW.book_id;
    END IF;
END //
DELIMITER ;


-- 显示创建结果
SELECT 'Database initialization completed successfully!' as message;

-- 显示表结构信息
SHOW TABLES;

-- 显示用户统计
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users,
    COUNT(CASE WHEN is_admin = 1 THEN 1 END) as admin_users
FROM users;

-- 显示图书统计
SELECT 
    COUNT(*) as total_books,
    SUM(stock_quantity) as total_stock,
    COUNT(DISTINCT category) as categories
FROM books;

-- 显示借阅统计
SELECT 
    COUNT(*) as total_borrows,
    COUNT(CASE WHEN status = 'borrowed' THEN 1 END) as current_borrows,
    COUNT(CASE WHEN status = 'returned' THEN 1 END) as returned_books
FROM borrows;
