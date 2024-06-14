class DamageFilters:
    def get_damage_data_filter(
        table: str,
        damage_type: str = None,
        damaged_part: str = None
    ):

        filters = []

        if damage_type:
            damage_types = [x.strip() for x in damage_type.split(',')]
            filters.append(table.damage_type.in_(damage_types))

        if damaged_part:
            damaged_parts = [x.strip() for x in damaged_part.split(',')]
            filters.append(table.damaged_part.in_(damaged_parts))

        return filters
