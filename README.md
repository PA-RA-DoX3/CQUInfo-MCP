# cquInfo-MCP

cquInfo-MCP 是一个基于 MCP（Model Control Protocol）框架开发的重庆大学信息服务工具，旨在为大模型提供一系列重庆大学校园信息查询服务。

## 功能
- 课程信息查询
- 考试安排查询
- 成绩查询

待实现的功能：
- 校园卡查询
- 图书馆查询

## API 文档

### 工具函数

#### login_cqu
登录重庆大学统一身份认证系统

输入参数：
- userid (string): 学号
- password (string): 密码

返回：登录状态信息

#### get_course_info
获取课程信息

输入参数：
- semester (string): 学期

返回：课程列表及详细信息

#### get_exam_info
获取考试安排

输入参数：
- semester (string): 学期

返回：考试安排列表

#### get_score
获取成绩信息

输入参数：
- semester (string): 学期（可选）

返回：成绩列表

## 使用方式
在支持MCP集成的应用中，向mcp_settings.json文件中添加以下配置：
```json
    "cquInfo": {
      "disabled": false,
      "timeout": 60,
      "command": "uv",
      "args": [
        "--directory",
        "D:\\Your\\File\\Location",
        "run",
        "cquInfo.py"
      ],
      "transportType": "stdio"
    }

```
## 感谢
感谢 https://github.com/321CQU/pymycqu 提供的 API 接口。