class SalesOrderConfig:
    """销售订单配置类"""
    
    # 订单类型配置
    ORDER_TYPES = {
        "STND": "标准销售",
        "THRD": "第三方销售",
        "CENT": "集中销售"
    }
    
    # 订单行类型配置
    ORDER_LINE_TYPES = {
        "NORM": "常规销售",
        "THRD": "三方销售",
        "CENT": "集中销售"
    }
    
    # 订单类型和订单行类型的组合配置
    ORDER_TYPE_LINE_COMBINATIONS = {
        "STND": ["NORM", "FREE", "SERV"],  # 标准销售可以使用常规销售、免费销售、服务销售
        "THRD": ["NORM", "FREE", "SERV"],  # 第三方销售可以使用常规销售、免费销售、服务销售
        "CENT": ["CENT", "FREE", "SERV"]   # 集中销售可以使用集中销售、免费销售、服务销售
    }
    
    # 订单类型ID映射
    ORDER_TYPE_IDS = {
        "STND": 2101001,  # 标准销售订单类型ID
        "THRD": 14010001,  # 第三方销售订单类型ID
        "CENT": 14012001   # 集中销售订单类型ID
    }
    
    # 订单行类型ID映射
    ORDER_LINE_TYPE_IDS = {
        "NORM": 2103001,  # 常规销售订单行类型ID
        "THRD": 2000005,  # 三方销售订单行类型ID
        "CENT": 2001002,  # 集中销售订单行类型ID
    }
    
    @classmethod
    def get_order_type_id(cls, order_type: str) -> int:
        """获取订单类型ID
        
        Args:
            order_type: 订单类型代码
            
        Returns:
            int: 订单类型ID
        """
        if order_type not in cls.ORDER_TYPE_IDS:
            raise ValueError(f"未知的订单类型: {order_type}")
        return cls.ORDER_TYPE_IDS[order_type]
    
    @classmethod
    def get_order_line_type_id(cls, order_type: str) -> int:
        """获取订单行类型ID
        
        Args:
            order_type: 订单类型代码
            
        Returns:
            int: 订单行类型ID
        """
        if order_type not in cls.ORDER_TYPE_LINE_COMBINATIONS:
            raise ValueError(f"未知的订单类型: {order_type}")
        
        line_type = cls.ORDER_TYPE_LINE_COMBINATIONS[order_type][0]
        if line_type not in cls.ORDER_LINE_TYPE_IDS:
            raise ValueError(f"未知的订单行类型: {line_type}")
            
        return cls.ORDER_LINE_TYPE_IDS[line_type] 