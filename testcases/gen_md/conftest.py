"""GEN_MD 模块清理注册。"""

from testcases.comm.cleanup_helpers import (
    pick_cleanup_column,
    safe_delete,
    safe_delete_like,
    table_exists,
)
from testcases.comm.cleanup_registry import get_module_db_config, register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _cleanup_gen_md() -> None:
    db = None
    iam_db = None

    try:
        db_config = get_module_db_config()
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 GEN_MD 数据清理")
            return

        iam_db_config = get_module_db_config("iam_db")

        db = DBManager(**db_config)
        if iam_db_config:
            iam_db = DBManager(**iam_db_config)

        # ── 条码 ──
        safe_delete(db, table="gen_barcode_md", where="obj_code like %s", params=["AT_%"])

        barcode_rule_col = pick_cleanup_column(db, "gen_barcode_rule_cf", ["org_code", "prefix", "code", "name"])
        if barcode_rule_col:
            safe_delete(db, table="gen_barcode_rule_cf", where=f"{barcode_rule_col} like %s", params=["AT_%"])
        else:
            Loggers.warning("gen_barcode_rule_cf 未找到可用清理列，已跳过")

        barcode_field_col = pick_cleanup_column(
            db, "gen_barcode_field_cf", ["org_code", "biz_field_key", "code", "name"]
        )
        if barcode_field_col:
            safe_delete(db, table="gen_barcode_field_cf", where=f"{barcode_field_col} like %s", params=["AT_%"])
        else:
            Loggers.warning("gen_barcode_field_cf 未找到可用清理列，已跳过")

        # ── 基础配置 ──
        safe_delete(db, table="gen_bank_cf", where="bank_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_sub_bank_cf", where="sub_bank_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_tax_type_cf", where="tax_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_timezone_type_cf", where="timezone_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_attr_cf", where="attr_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_index_md", where="gen_index_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_chara_class_md", where="code like %s", params=["AT_%"])
        safe_delete(db, table="gen_chara_md", where="code like %s", params=["AT_%"])

        # ── 币种 ──
        safe_delete(db, table="gen_curr_type_cf", where="curr_code like %s", params=["AT_%"])
        safe_delete_like(db, "gen_curr_formula_type_cf", ["code", "formula_code", "curr_formula_code"], "AT_%")
        safe_delete(db, table="gen_curr_exchange_rate_type_cf", where="type_code like %s", params=["AT_%"])

        # ── 工作中心 ──
        wc_code_col = pick_cleanup_column(db, "gen_wc_head_cf", ["wc_head_code", "code", "wcCode"])
        if wc_code_col:
            safe_delete(
                db,
                table="gen_wc_item_cf",
                where=f"gen_wc_head_id in (select id from gen_wc_head_cf where {wc_code_col} like %s)",
                params=["AT_%"],
            )
            safe_delete(db, table="gen_wc_head_cf", where=f"{wc_code_col} like %s", params=["AT_%"])
        else:
            Loggers.warning("gen_wc_head_cf 未找到可用清理列，已跳过 WC 相关清理")

        # ── 组织 ──
        safe_delete(db,
            table="org_struct_md",
            where="org_code like %s and org_dimension_code = 'ADM_ORG_GRP'",
            params=["AT_%"],
        )
        safe_delete(db, table="org_struct_md", where="org_code like %s", params=["AT_%"])
        safe_delete(db, table="org_identity_cf", where="code like %s", params=["AT_%"])
        safe_delete(db, table="org_business_type_cf", where="code like %s", params=["AT_OrgType%"])
        safe_delete(db, table="org_dimension_cf", where="org_dimension_code like %s", params=["AT_%"])

        # ── 员工（先删子表） ──
        safe_delete(db,
            table="pen_adjust_type_md",
            where="id in (select org_employee_id from org_employee_md where code like %s)",
            params=["AT_%"],
        )
        safe_delete(db,
            table="pen_adjust_md",
            where="id in (select org_employee_id from org_employee_md where code like %s)",
            params=["AT_%"],
        )
        safe_delete(db, table="org_employee_md", where="code like %s", params=["AT_%"])

        # ── 合作伙伴 ──
        safe_delete(db, table="gen_business_partner_md", where="code like %s", params=["AT_%"])
        safe_delete(db, table="gen_attachment_type_cf", where="attachment_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_attachment_procedure_head_cf", where="code like %s", params=["AT_%"])
        safe_delete(db, table="gen_partner_type_cf", where="partner_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_partner_procedure_head_cf", where="code like %s", params=["AT_%"])
        safe_delete(db, table="gen_business_partner_type_cf", where="code like %s", params=["AT_%"])
        safe_delete(db, table="gen_cust_tax_type_cf", where="tax_class_code like %s", params=["AT_%"])

        # ── 文本 / 资质 / 地址 ──
        safe_delete(db, table="gen_text_type_cf", where="text_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_text_procedure_head_cf", where="code like %s", params=["AT_%"])
        safe_delete(db, table="gen_qualifications_type_cf", where="code like %s", params=["AT_%"])
        safe_delete(db, table="gen_qualifications_procedure_head_cf", where="code like %s", params=["AT_%"])
        safe_delete(db, table="gen_addr_type_cf", where="addr_code like %s", params=["AT_%"])

        # ── 待办 ──
        if table_exists(db, "gen_daily_to_do"):
            safe_delete(db, table="gen_daily_to_do", where="title like %s", params=["AT_%"])
        else:
            Loggers.info("跳过清理 gen_daily_to_do: 表不存在")
        if table_exists(db, "gen_biz_to_do"):
            safe_delete(db, table="gen_biz_to_do", where="title like %s", params=["AT_%"])
        else:
            Loggers.info("跳过清理 gen_biz_to_do: 表不存在")

        # ── 字典 ──
        safe_delete(db, table="gen_dict_item_cf", where="dict_head_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_dict_head_cf", where="code like %s", params=["AT_%"])

        # ── 评分任务（先子后父） ──
        safe_delete(db,
            table="gen_survey_detail_md",
            where="survey_mission in (select id from gen_survey_mission_md where title like %s or title like %s)",
            params=["测试评分任务_%", "自动化_%"],
        )
        safe_delete(db,
            table="gen_survey_mission_item_md",
            where="gen_survey_mission_md_id in (select id from gen_survey_mission_md where title like %s or title like %s)",
            params=["测试评分任务_%", "自动化_%"],
        )
        safe_delete(db,
            table="gen_survey_mission_md",
            where="title like %s or title like %s",
            params=["测试评分任务_%", "自动化_%"],
        )

        # ── 标签 / 快递 / 国家 ──
        safe_delete(db, table="gen_label_md", where="name like %s", params=["测试标签_%"])
        safe_delete_like(db, "gen_express_com_md", ["express_code", "code", "express_com_code"], "AT_%")
        safe_delete(db, table="gen_coun_type_cf", where="coun_code like %s", params=["AT_%"])

        # ── 物料 ──
        safe_delete(db, table="gen_mat_cate_md", where="mat_cate_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_mat_type_cf", where="mat_type_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_brand_md", where="brand_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_mat_tax_type_cf", where="tax_class_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_mat_md", where="mat_code like %s", params=["AT_%"])

        # ── 计量单位 ──
        safe_delete(db,
            table="gen_uom_formula_type_cf",
            where="unit_id in(select id from gen_uom_type_cf where uom_code like %s)",
            params=["AT_%"],
        )
        safe_delete(db, table="gen_uom_type_cf", where="uom_code like %s", params=["AT_%"])

        # ── BOM ──
        safe_delete(db, table="gen_bom_head_md", where="bom_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_bom_item_type_cf", where="item_type like %s", params=["AT_%"])
        safe_delete(db, table="gen_bom_status_cf", where="status_code like %s", params=["AT_%"])
        safe_delete(db, table="gen_bom_use_cf", where="use_code like %s", params=["AT_%"])
        safe_delete_like(
            db, "gen_bom_item_supp_ind_cf",
            ["supp_ind_code", "supp_ind", "code", "item_supp_ind_code"],
            "AT_%",
        )

        # ── IAM ──
        if iam_db:
            safe_delete(iam_db, table="iam_user", where="username like %s", params=["AT_%"])

        Loggers.info("✅ GEN_MD 模块测试数据统一清理完成")
    except Exception as e:
        Loggers.error(f"❌ GEN_MD 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass
        if iam_db:
            try:
                iam_db.close()
            except Exception:
                pass


register_cleanup("gen_md_cleanup", _cleanup_gen_md, order=250)
