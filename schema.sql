CREATE DATABASE IF NOT EXISTS complaintiq_db;
USE complaintiq_db;

CREATE TABLE IF NOT EXISTS complaints (
    id INT PRIMARY KEY AUTO_INCREMENT,
    complaint_id VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL,
    complaint_text TEXT NOT NULL,
    attachment VARCHAR(255),
    category VARCHAR(100) NOT NULL,
    priority ENUM('High', 'Medium', 'Low') NOT NULL,
    sentiment ENUM('Positive', 'Neutral', 'Negative') NOT NULL,
    department VARCHAR(100) NOT NULL,
    status ENUM('Pending', 'In Progress', 'Resolved', 'Closed') NOT NULL DEFAULT 'Pending',
    admin_response TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

USE complaintiq_db;

INSERT INTO complaints (complaint_id, name, email, complaint_text, attachment, category, priority, sentiment, department, status, created_at, updated_at) VALUES
-- Billing Issue 
('CMP-20260402-ABC123', 'Aarav Sharma', 'aarav.sharma12@gmail.com', 'I was charged twice for my last payment of ₹1500. Please refund the duplicate amount immediately.', NULL, 'Billing Issue', 'High', 'Negative', 'Finance Department', 'Pending', '2026-04-01 14:30:00', '2026-04-01 14:30:00'),
('CMP-20260401-DEF456', 'Priya Mehta', 'priya.mehta25@yahoo.com', 'My invoice shows ₹800 extra charges that were never explained. Need clarification and correction.', NULL, 'Billing Issue', 'Medium', 'Negative', 'Finance Department', 'In Progress', '2026-04-01 10:15:00', '2026-04-02 09:20:00'),
('CMP-20260328-GHI789', 'Rohan Verma', 'rohan.verma88@outlook.com', 'Payment failed but ₹1200 was deducted. Transaction ID: TXN20260401ABC.', NULL, 'Billing Issue', 'High', 'Negative', 'Finance Department', 'Resolved', '2026-03-28 16:45:00', '2026-03-30 11:10:00'),
('CMP-20260325-JKL012', 'Sneha Patel', 'sneha.patel33@gmail.com', 'Refund for cancelled order #ORD12345 is still pending for 7 days.', NULL, 'Billing Issue', 'Medium', 'Neutral', 'Finance Department', 'Pending', '2026-03-25 09:20:00', '2026-03-25 09:20:00'),
('CMP-20260320-MNO345', 'Vikram Singh', 'vikram.singh77@hotmail.com', 'Bill shows subscription charges even after I cancelled last month.', NULL, 'Billing Issue', 'Low', 'Negative', 'Finance Department', 'Pending', '2026-03-20 13:50:00', '2026-03-20 13:50:00'),

-- Technical Issue 
('CMP-20260402-PQR678', 'Neha Joshi', 'neha.joshi45@gmail.com', 'Website crashes every time I try to login from Chrome browser. Error 500.', NULL, 'Technical Issue', 'High', 'Negative', 'IT Support', 'In Progress', '2026-04-02 11:25:00', '2026-04-02 15:30:00'),
('CMP-20260401-STU901', 'Arjun Nair', 'arjun.nair19@yahoo.com', 'Mobile app is not loading properly. Stuck on splash screen.', NULL, 'Technical Issue', 'High', 'Negative', 'IT Support', 'Pending', '2026-04-01 18:10:00', '2026-04-01 18:10:00'),
('CMP-20260330-VWX234', 'Kavya Iyer', 'kavya.iyer67@outlook.com', 'OTP verification fails after entering correct code. Tried 5 times.', NULL, 'Technical Issue', 'Medium', 'Negative', 'IT Support', 'Resolved', '2026-03-30 14:00:00', '2026-04-01 10:45:00'),
('CMP-20260327-YZA567', 'Rahul Khanna', 'rahul.khanna92@gmail.com', 'Complaint form freezes when submitting with attachment.', NULL, 'Technical Issue', 'Medium', 'Neutral', 'IT Support', 'Pending', '2026-03-27 16:30:00', '2026-03-27 16:30:00'),
('CMP-20260322-BCD890', 'Pooja Desai', 'pooja.desai28@hotmail.com', 'Dashboard shows "Server Error 503" when accessing reports.', NULL, 'Technical Issue', 'High', 'Negative', 'IT Support', 'In Progress', '2026-03-22 08:15:00', '2026-03-25 12:20:00'),

-- Service Complaint 
('CMP-20260402-EFG123', 'Ananya Shah', 'ananya.shah56@gmail.com', 'Customer support executive was rude and disconnected call abruptly.', NULL, 'Service Complaint', 'High', 'Negative', 'Customer Care', 'Pending', '2026-04-02 09:45:00', '2026-04-02 09:45:00'),
('CMP-20260401-HIJ456', 'Karan Gupta', 'karan.gupta34@yahoo.com', 'No response received even after 3 follow-up emails to support.', NULL, 'Service Complaint', 'Medium', 'Negative', 'Customer Care', 'In Progress', '2026-04-01 12:20:00', '2026-04-02 14:10:00'),
('CMP-20260329-KLM789', 'Meera Nair', 'meera.nair81@outlook.com', 'Service team promised callback within 2 hours but never called back.', NULL, 'Service Complaint', 'Low', 'Negative', 'Customer Care', 'Closed', '2026-03-29 17:30:00', '2026-03-31 11:25:00'),
('CMP-20260326-NOP012', 'Yash Patil', 'yash.patil49@gmail.com', 'Support chat agent gave incorrect information about policy.', NULL, 'Service Complaint', 'Medium', 'Neutral', 'Customer Care', 'Resolved', '2026-03-26 15:40:00', '2026-03-28 09:50:00'),
('CMP-20260321-QRS345', 'Simran Kaur', 'simran.kaur72@hotmail.com', 'Very poor service quality during weekend support hours.', NULL, 'Service Complaint', 'High', 'Negative', 'Customer Care', 'Pending', '2026-03-21 20:15:00', '2026-03-21 20:15:00'),

-- Delivery Issue 
('CMP-20260402-TUV678', 'Siddharth Rao', 'siddharth.rao13@gmail.com', 'Order #ORD56789 not delivered even after promised date of 28th March.', NULL, 'Delivery Issue', 'High', 'Negative', 'Logistics Department', 'Pending', '2026-04-02 13:20:00', '2026-04-02 13:20:00'),
('CMP-20260331-WXY901', 'Tanvi Chawla', 'tanvi.chawla91@yahoo.com', 'Courier tracking shows "Out for Delivery" since 3 days but no delivery.', NULL, 'Delivery Issue', 'High', 'Negative', 'Logistics Department', 'In Progress', '2026-03-31 10:50:00', '2026-04-01 16:30:00'),
('CMP-20260328-ZAB234', 'Nisha Bhat', 'nisha.bhat65@outlook.com', 'Package marked as delivered but I never received it.', NULL, 'Delivery Issue', 'High', 'Negative', 'Logistics Department', 'Resolved', '2026-03-28 11:15:00', '2026-03-30 14:45:00'),
('CMP-20260324-CDE567', 'Arjun Soni', 'arjun.soni37@gmail.com', 'Wrong address entered by delivery team, package returned to hub.', NULL, 'Delivery Issue', 'Medium', 'Neutral', 'Logistics Department', 'Pending', '2026-03-24 18:25:00', '2026-03-24 18:25:00'),
('CMP-20260319-FGH890', 'Riya Malhotra', 'riya.malhotra84@hotmail.com', 'Delivery delayed 5 days beyond committed timeline.', NULL, 'Delivery Issue', 'Medium', 'Negative', 'Logistics Department', 'Closed', '2026-03-19 14:10:00', '2026-03-22 09:30:00'),

-- Account Problem 
('CMP-20260402-IJK123', 'Aditya Kumar', 'aditya.kumar29@gmail.com', 'Account locked after 3 failed login attempts. Need to reset.', NULL, 'Account Problem', 'High', 'Negative', 'Customer Support', 'Pending', '2026-04-02 16:40:00', '2026-04-02 16:40:00'),
('CMP-20260401-LMN456', 'Ishita Verma', 'ishita.verma71@yahoo.com', 'Password reset link expired immediately after receiving email.', NULL, 'Account Problem', 'Medium', 'Negative', 'Customer Support', 'In Progress', '2026-04-01 07:30:00', '2026-04-02 11:20:00'),
('CMP-20260330-OPQ789', 'Vivaan Patel', 'vivaan.patel52@outlook.com', 'Email verification failed during account creation process.', NULL, 'Account Problem', 'Medium', 'Neutral', 'Customer Support', 'Resolved', '2026-03-30 12:45:00', '2026-04-01 15:10:00'),
('CMP-20260327-RST012', 'Divya Reddy', 'divya.reddy96@gmail.com', 'Cannot update mobile number in profile section.', NULL, 'Account Problem', 'Low', 'Negative', 'Customer Support', 'Pending', '2026-03-27 19:15:00', '2026-03-27 19:15:00'),
('CMP-20260323-UVW345', 'Kunal Mishra', 'kunal.mishra68@hotmail.com', 'Account shows suspended status without any notification.', NULL, 'Account Problem', 'High', 'Negative', 'Customer Support', 'Pending', '2026-03-23 10:20:00', '2026-03-23 10:20:00');