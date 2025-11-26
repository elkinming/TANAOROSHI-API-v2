"""
ユーザーリポジトリ

ユーザーテーブルへのデータアクセス処理
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import or_, cast, String
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError
from sqlmodel import Session, select
from app.models.user import User
from app.schemas.user import UserBase


class UserRepository:
    """ユーザーリポジトリクラス"""

    def __init__(self, session: Session):
        """
        リポジトリを初期化する

        Args:
            session: データベースセッション
        """
        self.session = session

    def get_all(
        self,
        search_keyword: Optional[str] = None
    ) -> List[User]:
        """
        ユーザーのリストを取得する

        Args:
            search_keyword: 全カラムで曖昧検索（オプション）

        Returns:
            List[User]: ユーザーのリスト
        """
        statement = select(User)

        # 検索キーワードでフィルタ
        if search_keyword:
            like = f"%{search_keyword}%"
            statement = statement.where(
                or_(
                    # User.id.ilike(like),
                    User.name.ilike(like),
                    User.lastname.ilike(like),
                    cast(User.age, String).ilike(like),
                    User.country.ilike(like),
                    User.home_address.ilike(like),
                )
            )

        # 名前と姓でソート
        statement = statement.order_by(User.name, User.lastname)

        return list(self.session.exec(statement).all())

    def get_by_id(self, user_id: Optional[str]) -> Optional[User]:
        """
        ユーザーIDでユーザーを取得する

        Args:
            user_id: ユーザーID

        Returns:
            Optional[User]: ユーザー（見つからない場合はNone）
        """
        if user_id is None:
            return None
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first()

    def create_user(self, user_data: UserBase) -> User:
        """
        ユーザーを作成する

        Args:
            user_data: 作成するユーザーデータ

        Returns:
            User: 作成されたユーザー
        """
        db_item = User(**user_data.model_dump())
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def create_user_batch(self, user_data_list: List[UserBase]) -> List[User]:
        """
        ユーザーを一括作成する

        Args:
            user_data_list: 作成するユーザーデータのリスト

        Returns:
            List[User]: 作成されたユーザーのリスト
        """
        db_items = []
        for user_data in user_data_list:
            db_item = User(**user_data.model_dump())
            self.session.add(db_item)
            db_items.append(db_item)

        self.session.commit()

        # Refresh all items
        for db_item in db_items:
            self.session.refresh(db_item)

        return db_items

    def update_user(self, user_data: UserBase) -> Optional[User]:
        """
        ユーザーを更新する

        Args:
            user_data: 更新するユーザーデータ

        Returns:
            Optional[User]: 更新されたユーザー（見つからない場合はNone）
        """
        db_item = self.get_by_id(user_data.id)
        if not db_item:
            return None

        # 更新データを適用
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)

        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def update_user_batch(self, user_data_list: List[UserBase]) -> Dict[str, Any]:
        """
        ユーザーを一括更新する

        Args:
            user_data_list: 更新するユーザーデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[User] - 更新されたユーザーのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        ok_records = []
        error_records: List[Dict[str, Any]] = []

        for user_data in user_data_list:
            db_item = self.get_by_id(user_data.id)
            if not db_item:
                error_records.append({
                    "level": "E",
                    "message": "Record not found",
                    "detail": "A record with the specified ID does not exist",
                    "code": "NotFoundError",
                    "record": user_data.model_dump()
                })
                continue

            # 各アイテムを個別に処理するためにセーブポイントを使用
            savepoint = self.session.begin_nested()
            try:
                # 更新データを適用
                update_data = user_data.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(db_item, field, value)

                self.session.add(db_item)
                self.session.flush()

                savepoint.commit()
                ok_records.append(db_item)
            except Exception as e:
                # エラー情報を抽出
                error_code = type(e).__name__
                error_message = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
                error_detail = str(e)

                # SQLAlchemyエラーの場合、より詳細な情報を取得
                if isinstance(e, (IntegrityError, DataError, DatabaseError)):
                    if hasattr(e, 'orig') and e.orig:
                        error_detail = str(e.orig)
                        # PostgreSQLエラーの場合、pgcodeを取得
                        if hasattr(e.orig, 'pgcode'):
                            error_code = f"PG{e.orig.pgcode}" if e.orig.pgcode else error_code

                # エラーが発生したレコードを保存
                error_records.append({
                    "level": "E",
                    "message": error_message,
                    "detail": error_detail,
                    "code": error_code,
                    "record": user_data.model_dump()
                })
                # セーブポイントをロールバック（このアイテムのみ）
                savepoint.rollback()

        # エラーが発生した場合はコミットせずにロールバック
        if error_records:
            # 全ての変更をロールバック
            self.session.rollback()
        else:
            # エラーがない場合のみコミット
            if ok_records:
                self.session.commit()
                # Refresh all items
                for db_item in ok_records:
                    self.session.refresh(db_item)

        # ok_recordsとerror_recordsを含む辞書を返す
        return {
            "ok_records": ok_records,
            "error_records": error_records
        }

    def create_multiple_user(self, user_data_list: List[UserBase]) -> Dict[str, Any]:
        """
        ユーザーを一括作成する

        Args:
            user_data_list: 作成するユーザーデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[User] - 作成されたユーザーのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        ok_records = []
        error_records: List[Dict[str, Any]] = []

        for user_data in user_data_list:
            # 各アイテムを個別に処理するためにセーブポイントを使用
            savepoint = self.session.begin_nested()
            try:
                # 新規レコードを作成
                db_item = User(**user_data.model_dump())
                print(user_data.model_dump())
                print(db_item)
                self.session.add(db_item)
                self.session.flush()

                savepoint.commit()
                ok_records.append(db_item)
            except Exception as e:
                # エラー情報を抽出
                error_code = type(e).__name__
                error_message = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
                error_detail = str(e)

                # SQLAlchemyエラーの場合、より詳細な情報を取得
                if isinstance(e, (IntegrityError, DataError, DatabaseError)):
                    if hasattr(e, 'orig') and e.orig:
                        error_detail = str(e.orig)
                        # PostgreSQLエラーの場合、pgcodeを取得
                        if hasattr(e.orig, 'pgcode'):
                            error_code = f"PG{e.orig.pgcode}" if e.orig.pgcode else error_code

                # エラーが発生したレコードを保存
                error_records.append({
                    "level": "E",
                    "message": error_message,
                    "detail": error_detail,
                    "code": error_code,
                    "record": user_data.model_dump()
                })
                # セーブポイントをロールバック（このアイテムのみ）
                savepoint.rollback()

        # エラーが発生した場合はコミットせずにロールバック
        if error_records:
            # 全ての変更をロールバック
            self.session.rollback()
        else:
            # エラーがない場合のみコミット
            if ok_records:
                self.session.commit()
                # Refresh all items
                for db_item in ok_records:
                    self.session.refresh(db_item)

        # ok_recordsとerror_recordsを含む辞書を返す
        return {
            "ok_records": ok_records,
            "error_records": error_records
        }

    def delete_multiple_user(self, user_data_list: List[UserBase]) -> Dict[str, Any]:
        """
        ユーザーを一括削除する

        Args:
            user_data_list: 削除するユーザーデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[User] - 削除されたユーザーのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        ok_records = []
        error_records: List[Dict[str, Any]] = []

        for user_data in user_data_list:
            # 既存レコードのチェック
            db_item = self.get_by_id(user_data.id)
            if not db_item:
                # レコードが見つからない場合はエラーレコードとして追加
                error_records.append({
                    "level": "E",
                    "message": "Record not found",
                    "detail": "A record with the specified ID does not exist",
                    "code": "NotFoundError",
                    "record": user_data.model_dump()
                })
                continue

            # 各アイテムを個別に処理するためにセーブポイントを使用
            savepoint = self.session.begin_nested()
            try:
                # レコードを削除
                self.session.delete(db_item)
                self.session.flush()

                savepoint.commit()
                ok_records.append(db_item)
            except Exception as e:
                # エラー情報を抽出
                error_code = type(e).__name__
                error_message = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
                error_detail = str(e)

                # SQLAlchemyエラーの場合、より詳細な情報を取得
                if isinstance(e, (IntegrityError, DataError, DatabaseError)):
                    if hasattr(e, 'orig') and e.orig:
                        error_detail = str(e.orig)
                        # PostgreSQLエラーの場合、pgcodeを取得
                        if hasattr(e.orig, 'pgcode'):
                            error_code = f"PG{e.orig.pgcode}" if e.orig.pgcode else error_code

                # エラーが発生したレコードを保存
                error_records.append({
                    "level": "E",
                    "message": error_message,
                    "detail": error_detail,
                    "code": error_code,
                    "record": user_data.model_dump()
                })
                # セーブポイントをロールバック（このアイテムのみ）
                savepoint.rollback()

        # エラーが発生した場合はコミットせずにロールバック
        if error_records:
            # 全ての変更をロールバック
            self.session.rollback()
        else:
            # エラーがない場合のみコミット
            if ok_records:
                self.session.commit()

        # ok_recordsとerror_recordsを含む辞書を返す
        return {
            "ok_records": ok_records,
            "error_records": error_records
        }

