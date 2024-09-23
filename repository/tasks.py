import datetime
from sqlalchemy import func
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload

from models import Task, User
from datetime import date, datetime
from database import async_session
from models.tasks import CategoryTask


class TaskRepository:
    dict_categories = {
            'subscribe': 1,
            'games': 2,
            'watch': 3,
            'like': 4,
            'comment': 5,
            'save': 6,
            'bonus': 7
    }
    @classmethod
    async def get_task_by_id(cls, task_id: int, session: async_session) -> Task:
        """
        Метод для получения задания из БД по его task_id
        :param task_id: ID задания в БД
        :param session: Асинхронная сессия
        :return: инстанс задания
        :rtype: Task
        """
        result = await session.execute(
                select(Task)
                .where(Task.id == task_id)
        )
        task = result.scalars().first()
        return task

    @classmethod
    async def add_task(cls, user: User, task: Task, session: async_session) -> None:
        """
        Добавление выполненного задания пользователя
        :param user: инстанс Пользователя
        :param task: инстанс задания
        :param session: Асинхронная сессия
        :return: None
        """
        if task not in user.tasks:
            user.tasks.append(task)
            user.count_tasks += 1
            await session.commit()

    @classmethod
    async def create_task(cls, url: str, description: str, type_task: str,
                          date: str, session: async_session) -> bool:
        """
        Метод для создания нового задания
        :param url: ссылка на задание
        :param description: описание задания
        :param type_task: тип задания
        :param date: дата, до которой действует
        :param session: Асинхронная сессия
        :return: bool
        """
        new_task = Task(
                url=url,
                description=description,
                category_id=cls.dict_categories[type_task],
                date_limit=datetime.strptime(date, '%d.%m.%Y')
        )
        session.add(new_task)
        await session.commit()
        return True

    @classmethod
    async def get_tasks_by_type(cls, type_task: str, session: async_session) -> list[Task]:
        """
        Получить задания заданного типа
        :param type_task: тип задания
        :param session: Асинхронная сессия
        :return: список заданий
        :rtype: list[Task]
        """
        result = await session.execute(
                select(Task)
                .where(Task.category_id == cls.dict_categories[type_task])
        )
        tasks = result.scalars().all()
        return tasks

    @classmethod
    async def get_categories_with_tasks(cls, session: async_session) -> list[CategoryTask]:
        """
        Получить список категорий задач вместе с задачами, относящимся к этим категориям
        :param session: Асинхронная сессия
        :return: список категорий
        :rtype: list[CategoryTask]
        """
        result = await session.execute(
                select(CategoryTask)
                .options(joinedload(CategoryTask.tasks))
        )
        categories = result.scalars().unique().all()
        return categories
    @classmethod
    async def get_tasks_with(cls, session: async_session) -> list[CategoryTask]:
        """
        Получить список категорий задач вместе с задачами, относящимся к этим категориям
        :param session: Асинхронная сессия
        :return: список категорий
        :rtype: list[CategoryTask]
        """
        result = await session.execute(
                select(CategoryTask)
                .options(joinedload(CategoryTask.tasks))
        )
        categories = result.scalars().all()
        return categories
    @classmethod
    async def get_all_tasks(cls, session) -> list[Task]:
        """
        Получить все активные задания
        :param session: Асинхронная сессия
        :return: список заданий
        :rtype: list[Task
        """
        today = datetime.today()
        result = await session.execute(
                select(Task)
                .where(Task.date_limit >= today)
        )
        tasks = result.scalars().all()
        return tasks

    @classmethod
    async def get_count_tasks(cls, session: async_session, date: date) -> int:
        """
        Метод ддя получения количества активных задач за период date
        :param session: Асинхронная сессия
        :param date: Дата
        :return: Количество задач
        :rtype: int
        """
        count_tasks = await session.execute(
                select(func.count(Task.id))
                .where(Task.date_limit >= date)
        )
        return count_tasks.scalar()

    @classmethod
    async def get_task_by_url(cls, session: async_session, url_task: str) -> Task:
        """
        Получение задачи по её url(ссылке)
        :param session: Асинхронная сессия
        :param url_task: Ссылка на задачу
        :return: Задача
        :rtype: Task
        """
        result = await session.execute(
                select(Task).where(Task.url == url_task)
        )
        task = result.scalars().first()
        return task

    @classmethod
    async def task_delete(cls, session: async_session, task_id: int) -> None:
        """
        Метод для удаления задачи по её task_id в базе данных
        :param session: Асинхронная сессия
        :param task_id: ID задачи в БД
        :return: None
        """
        query = delete(Task).where(Task.id == task_id)
        await session.execute(query)
        await session.commit()

    @classmethod
    async def get_tasks_by_celery(cls, session: async_session) -> int:
        """
        Функция для получения всех заданий в базе данных
        Дата действия которых уже закончилась
        :param session: Асинхронная сессия
        :return: Все задания
        :rtype: int
        """
        today = datetime.today().date()
        query_tasks = await session.execute(
                select(Task)
                .where(Task.date_limit < today)
        )
        tasks_all = query_tasks.result.scalars().all()
        return tasks_all

    @classmethod
    async def task_delete_by_celery(cls, session: async_session, task_id: int) -> None:
        """
        Метод для удаления задачи по её task_id
        :param session: Асинхронная сессия
        :param task_id: ID задания в БД
        :return: None
        """
        stmt = (
                delete(Task).
                where(Task.id == task_id)
        )
        await session.execute(stmt)
        await session.commit()
