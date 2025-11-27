"""
得意先マスタリポジトリ

得意先マスタテーブルへのデータアクセス処理
"""
from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy import or_, cast, String
from sqlalchemy.exc import IntegrityError, DataError, DatabaseError
from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.koujyou_master import KoujyouMaster
from app.schemas.koujyou_master import KoujyouMasterBase


class InventoryRepository:
    """得意先マスタリポジトリクラス"""

    def __init__(self, session: Session):
        """
        リポジトリを初期化する

        Args:
            session: データベースセッション
        """
        self.session = session

    def get_all(
        self,
        previous_factory_code: Optional[str] = None,
        product_factory_code: Optional[str] = None,
        search_keyword: Optional[str] = None
    ) -> List[KoujyouMaster]:
        """
        得意先マスタのリストを取得する

        Args:
            skip: スキップする件数
            limit: 取得する最大件数
            corporate_cd: 法人コードでフィルタ（オプション）
            toku_cd: 得意先コードでフィルタ（オプション）
            toku_name: 得意先名称で曖昧検索（オプション）

        Returns:
            List[CustomMaster]: 得意先マスタのリスト
        """
        statement = select(KoujyouMaster)

        # フィルタ条件を追加
        if previous_factory_code:
            statement = statement.where(KoujyouMaster.previous_factory_code.ilike(f"%{previous_factory_code}%"))
        if product_factory_code:
            statement = statement.where(KoujyouMaster.product_factory_code.ilike(f"%{product_factory_code}%"))
        if search_keyword:
            like = f"%{search_keyword}%"
            statement = statement.where(
                or_(
                    KoujyouMaster.previous_factory_code.ilike(like),
                    KoujyouMaster.company_code.ilike(like),
                    KoujyouMaster.product_factory_code.ilike(like),
                    cast(KoujyouMaster.start_operation_date, String).ilike(like),
                    cast(KoujyouMaster.end_operation_date, String).ilike(like),
                    KoujyouMaster.previous_factory_name.ilike(like),
                    KoujyouMaster.product_factory_name.ilike(like),
                    KoujyouMaster.material_department_code.ilike(like),
                    KoujyouMaster.environmental_information.ilike(like),
                    KoujyouMaster.authentication_flag.ilike(like),
                    KoujyouMaster.group_corporate_code.ilike(like),
                    KoujyouMaster.integration_pattern.ilike(like),
                    KoujyouMaster.hulftid.ilike(like),
                )
            )

        return list(self.session.exec(statement).all())

    def __init__(self, session: Session):
        """
        リポジトリを初期化する

        Args:
            session: データベースセッション
        """
        self.session = session

    def get_time_related_records( self, koujyou_master_data ) -> List[KoujyouMaster]:
        """
        時間関連の工場マスタレコードを取得する

        指定された工場マスタデータと同じ工場コード（従来工場コード、商品工場コード）と
        会社コードを持つ全てのレコードを取得します。時間ロジックチェックなどで使用されます。

        Args:
            koujyou_master_data (KoujyouMasterBase): 基準となる工場マスタデータ

        Returns:
            List[KoujyouMaster]: 同じ工場コードと会社コードを持つ工場マスタレコードのリスト
        """
        statement = select(KoujyouMaster).where(
            KoujyouMaster.previous_factory_code == koujyou_master_data.previous_factory_code,
            KoujyouMaster.product_factory_code == koujyou_master_data.product_factory_code,
            KoujyouMaster.company_code == koujyou_master_data.company_code
        )

        return list(self.session.exec(statement).all())

    def get_by_unique_keys(self, koujyou_master_data) -> Optional["KoujyouMaster"]:
        """
        PKが一致する工場マスタレコードが存在するか確認する

        Args:
            koujyou_master_data (KoujyouMasterBase): チェック対象の工場マスタデータ

        Returns:
            Optional[KoujyouMaster]: 該当する場合はマスタのレコード、なければNone
        """
        # PK: previous_factory_code, product_factory_code, start_operation_date, company_code, end_operation_date
        statement = select(KoujyouMaster).where(
            KoujyouMaster.previous_factory_code == koujyou_master_data.previous_factory_code,
            KoujyouMaster.product_factory_code == koujyou_master_data.product_factory_code,
            KoujyouMaster.start_operation_date == koujyou_master_data.start_operation_date,
            KoujyouMaster.company_code == koujyou_master_data.company_code,
            KoujyouMaster.end_operation_date == koujyou_master_data.end_operation_date,
        )
        return self.session.exec(statement).first()

    def create_koujyou_master(self, koujyou_master_data):
        """
        工場マスタを作成する

        Args:
            koujyou_master_data (KoujyouMasterBase): 作成する工場マスタデータ

        Returns:
            KoujyouMaster: 作成された工場マスタ
        """
        db_item = KoujyouMaster(**koujyou_master_data.model_dump())
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def create_koujyou_master_batch(self, koujyou_master_data_list: List[KoujyouMasterBase]):
        """
        工場マスタを一括作成する

        Args:
            koujyou_master_data_list: 作成する工場マスタデータのリスト

        Returns:
            List[KoujyouMaster]: 作成された工場マスタのリスト
        """
        db_items = []
        for koujyou_master_data in koujyou_master_data_list:
            db_item = KoujyouMaster(**koujyou_master_data.model_dump())
            self.session.add(db_item)
            db_items.append(db_item)

        self.session.commit()

        # Refresh all items
        for db_item in db_items:
            self.session.refresh(db_item)

        return db_items

    def update_koujyou_master(self, koujyou_master_data):
        """
        工場マスタを更新する

        Args:
            koujyou_master_data (KoujyouMasterBase): 更新する工場マスタデータ

        Returns:
            Optional[KoujyouMaster]: 更新された工場マスタ（見つからない場合はNone）
        """
        db_item = self.get_by_unique_keys(koujyou_master_data)
        if not db_item:
            return None

        # 更新データを適用
        update_data = koujyou_master_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)

        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item

    def update_koujyou_master_batch(self, koujyou_master_data_list: List[KoujyouMasterBase]):
        """
        工場マスタを一括更新する

        Args:
            koujyou_master_data_list: 更新する工場マスタデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[KoujyouMaster] - 更新された工場マスタのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        ok_records = []
        error_records: List[Dict[str, Any]] = []

        for koujyou_master_data in koujyou_master_data_list:
            db_item = self.get_by_unique_keys(koujyou_master_data)
            if not db_item:
                continue

            # 各アイテムを個別に処理するためにセーブポイントを使用
            savepoint = self.session.begin_nested()
            try:
                # 更新データを適用
                update_data = koujyou_master_data.model_dump(exclude_unset=True)
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
                    "record": koujyou_master_data.model_dump()
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

    def create_multiple_koujyou_master(self, koujyou_master_data_list: List[KoujyouMasterBase]):
        """
        工場マスタを一括作成する

        Args:
            koujyou_master_data_list: 作成する工場マスタデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[KoujyouMaster] - 作成された工場マスタのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        ok_records = []
        error_records: List[Dict[str, Any]] = []

        for koujyou_master_data in koujyou_master_data_list:
            # 既存レコードのチェック
            # existing_item = self.get_by_unique_keys(koujyou_master_data)
            # if existing_item:
            #     # 既に存在する場合はエラーレコードとして追加
            #     error_records.append({
            #         "level": "E",
            #         "message": "Record already exists",
            #         "detail": "A record with the same primary key already exists",
            #         "code": "DuplicateKeyError",
            #         "record": koujyou_master_data.model_dump()
            #     })
            #     continue

            # 各アイテムを個別に処理するためにセーブポイントを使用
            savepoint = self.session.begin_nested()
            try:
                # 新規レコードを作成
                db_item = KoujyouMaster(**koujyou_master_data.model_dump())
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
                    "record": koujyou_master_data.model_dump()
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

    def delete_multiple_koujyou_master(self, koujyou_master_data_list: List[KoujyouMasterBase]):
        """
        工場マスタを一括削除する

        Args:
            koujyou_master_data_list: 削除する工場マスタデータのリスト

        Returns:
            Dict[str, Any]: 辞書型で以下のキーを含む:
                - ok_records: List[KoujyouMaster] - 削除された工場マスタのリスト
                - error_records: List[Dict[str, Any]] - エラーが発生したレコードのリスト
        """
        ok_records = []
        error_records: List[Dict[str, Any]] = []

        for koujyou_master_data in koujyou_master_data_list:
            # 既存レコードのチェック
            db_item = self.get_by_unique_keys(koujyou_master_data)
            if not db_item:
                # レコードが見つからない場合はエラーレコードとして追加
                error_records.append({
                    "level": "E",
                    "message": "Record not found",
                    "detail": "A record with the specified primary key does not exist",
                    "code": "NotFoundError",
                    "record": koujyou_master_data.model_dump()
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
                    "record": koujyou_master_data.model_dump()
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


    # def create(self, custom_master_data: CustomMasterCreate) -> CustomMaster:
    #     """
    #     得意先マスタを作成する

    #     Args:
    #         custom_master_data: 作成する得意先マスタデータ

    #     Returns:
    #         CustomMaster: 作成された得意先マスタ
    #     """
    #     db_item = CustomMaster(**custom_master_data.model_dump())
    #     self.session.add(db_item)
    #     self.session.commit()
    #     self.session.refresh(db_item)
    #     return db_item

    # def get_by_id(
    #     self,
    #     corporate_cd: str,
    #     toku_cd: str,
    #     ty_date_from: date
    # ) -> Optional[CustomMaster]:
    #     """
    #     主キーで得意先マスタを取得する

    #     Args:
    #         corporate_cd: 法人コード
    #         toku_cd: 得意先コード
    #         ty_date_from: 適用開始日

    #     Returns:
    #         Optional[CustomMaster]: 得意先マスタ（見つからない場合はNone）
    #     """
    #     statement = select(CustomMaster).where(
    #         CustomMaster.corporate_cd == corporate_cd,
    #         CustomMaster.toku_cd == toku_cd,
    #         CustomMaster.ty_date_from == ty_date_from
    #     )
    #     return self.session.exec(statement).first()

    # def update(
    #     self,
    #     corporate_cd: str,
    #     toku_cd: str,
    #     ty_date_from: date,
    #     custom_master_data: CustomMasterUpdate
    # ) -> Optional[CustomMaster]:
    #     """
    #     得意先マスタを更新する

    #     Args:
    #         corporate_cd: 法人コード
    #         toku_cd: 得意先コード
    #         ty_date_from: 適用開始日
    #         custom_master_data: 更新するデータ

    #     Returns:
    #         Optional[CustomMaster]: 更新された得意先マスタ（見つからない場合はNone）
    #     """
    #     db_item = self.get_by_id(corporate_cd, toku_cd, ty_date_from)
    #     if not db_item:
    #         return None

    #     # 更新データを適用
    #     update_data = custom_master_data.model_dump(exclude_unset=True)
    #     for field, value in update_data.items():
    #         setattr(db_item, field, value)

    #     # 更新日時を自動設定
    #     from datetime import datetime
    #     db_item.upd_dtime = datetime.now()

    #     self.session.add(db_item)
    #     self.session.commit()
    #     self.session.refresh(db_item)
    #     return db_item

    # def delete(
    #     self,
    #     corporate_cd: str,
    #     toku_cd: str,
    #     ty_date_from: date
    # ) -> bool:
    #     """
    #     得意先マスタを削除する

    #     Args:
    #         corporate_cd: 法人コード
    #         toku_cd: 得意先コード
    #         ty_date_from: 適用開始日

    #     Returns:
    #         bool: 削除成功時はTrue、見つからない場合はFalse
    #     """
    #     db_item = self.get_by_id(corporate_cd, toku_cd, ty_date_from)
    #     if not db_item:
    #         return False

    #     self.session.delete(db_item)
    #     self.session.commit()
    #     return True

