# 标准库导入
import re
from typing import Any, Dict, List, Optional
from datetime import date

# 第三方库导入
from anyio.abc import UnreliableObjectReceiveStream
from mycqu.card.tools import get_card_raw
from mycqu.score.tools import get_gpa_ranking_raw, get_score_raw
import requests
from requests import Session, session, sessions
import httpx
from mcp.server.fastmcp import FastMCP, Context

# mycqu 相关导入
from mycqu import CQUSession, CourseTimetable, GpaRanking, Score
from mycqu.exam import Exam
from mycqu.mycqu import access_mycqu
from mycqu.auth import login, NeedCaptcha



# 初始化 FastMCP server
mcp = FastMCP("CQU Info Service")

# 常量定义
AUTH_URL = "https://sso.cqu.edu.cn/login"
API_BASE = "https://my.cqu.edu.cn/api"

# 会话管理
user_sessions = {}

# 工具函数
@mcp.tool()
async def login_cqu( userid:str ,password: str, ctx: Context) -> str:
    """
    登录重庆大学统一身份认证系统
    Args:
        userid (str): 学号
        password (str): 密码
    returns:
        str: 登录结果
    """
    # TODO: 实现登录逻辑
    try:
        s = requests.Session()
        login(s, userid, password)
        access_mycqu(s)
        user_sessions[userid] = s
        return "登录成功"
    except NeedCaptcha as e:
        # 处理需要验证码的情况
        with open("captcha.jpg", "wb") as file:
            file.write(e.image)
        print("输入 captcha.jpg 处的验证码并回车: ", end="")
        e.after_captcha(input())
    except Exception as e:
        return f"登录失败: {str(e)}"


@mcp.tool()
async def get_exams(userid: str) -> str:
    """
    获取所有的考试安排
    Args:
        userid (str): 学号

    Returns:
        str: 考试科目，考试地点，考试座位号，考试时间
    """
    # TODO: 实现考试安排查询
    if userid not in user_sessions:
        return "请先使用 login_cqu 登录"
    try:
        session = user_sessions[userid]
        exams = Exam.fetch(session,userid)

        if not exams:
            return "没有考试安排"

        result = "考试安排如下：\n "
        for i , exam in enumerate(exams, 1):
            result += f"{i}. 科目: {exam.course.name}, 地点: {exam.room}, 座位号: {exam.seat_num}, 时间: {exam.start_time} - {exam.end_time}\n"
        return result
    except Exception as e:
        return f"获取考试安排失败: {str(e)}"

@mcp.tool()
async def get_schedule(userid: str, start_week: int, end_week: int) -> str:
    """
    获取指定周次区间的课程安排
    如果要查绚所有的课程安排，可以将 start_week 和 end_week 设置为 0
    Args:
        userid (str): 学号
        start_week (int): 起始周次
        end_week (int): 结束周次

    Returns:
        str: 课程名称 课程学分 课程地点 课程时间 课程教师
    """
    if userid not in user_sessions:
        return "请先使用 login_cqu 登录"
    try:
        session = user_sessions[userid]
        timetables = CourseTimetable.fetch(session, userid)
        if not timetables:
            return "没有课程安排"

        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        result = "所有课程安排：\n" if start_week == 0 and end_week == 0 else f"第{start_week}周到第{end_week}周的课程安排：\n"
        found_courses = False

        for timetable in timetables:
            # 检查课程是否在指定周次区间内，如果start_week和end_week都为0，则显示所有课程
            if start_week == 0 and end_week == 0:
                in_range = True
            else:
                in_range = False
                for week in timetable.weeks:
                    if (week.start <= end_week and week.end >= start_week):
                        in_range = True
                        break         
            if in_range:
                found_courses = True
                result += f"\n课程：{timetable.course.name}\n"
                result += f"地点：{timetable.classroom_name}，学分：{timetable.course.credit}，教师：{timetable.course.instructor}\n"
                
                # 添加上课周次信息
                weeks_str = []
                for week in timetable.weeks:
                    if week.start == week.end:
                        weeks_str.append(f"第{week.start}周")
                    else:
                        weeks_str.append(f"第{week.start}-{week.end}周")
                result += f"周次：{', '.join(weeks_str)}\n"
                
                # 添加上课时间信息
                if timetable.day_time:
                    result += (f"时间：周{weekdays[timetable.day_time.weekday]} "
                             f"第{timetable.day_time.period.start}-{timetable.day_time.period.end}节\n")
                elif timetable.whole_week:
                    result += "时间：全周时间\n"
                else:
                    result += "时间：无明确时间\n"

        if not found_courses:
            return "没有课程安排" if start_week == 0 and end_week == 0 else f"第{start_week}周到第{end_week}周没有课程安排"
            
        return result
    except Exception as e:
        return f"获取课程安排失败: {str(e)}"


@mcp.tool()
async def get_grades(userid:str) -> str:
    """获取所有学科的所有成绩"""
    # TODO: 实现成绩查询
    if userid not in user_sessions:
        return "请先使用 login_cqu 登录"
    try:
        session = user_sessions[userid]
        scores = Score.fetch(session)
        if not scores:
            return "没有成绩"
        result = "成绩如下：\n"
        for score in scores:
            result += f"\n课程名称：{score.course.name}，课程学分：{score.course.credit}\n"
            result += f"学期：{str(score.session)}，教师：{score.course.instructor}\n"
            result += f"成绩：{score.score}\n"
        return result
    except Exception as e:
        return f"获取成绩失败: {str(e)}"

@mcp.tool()
async def get_gpa(userid:str) -> str:
    """获取所有学科的所有成绩"""
    # TODO: 实现成绩查询
    if userid not in user_sessions:
        return "请先使用 login_cqu 登录"
    try:
        session = user_sessions[userid]
        gpaRanking = GpaRanking.fetch(session)
        if not gpaRanking:
            return "没有成绩"
        result = "成绩如下：\n"
        result += f"\n总绩点：{gpaRanking.gpa}，专业排名：{gpaRanking.major_ranking}，年级排名：{gpaRanking.grade_ranking}，"
        result += f"班级排名：{gpaRanking.class_ranking}，加权平均分：{gpaRanking.weighted_avg}\n"
        return result
    except Exception as e:
        return f"获取成绩失败: {str(e)}"

if __name__ == "__main__":
    mcp.run()
