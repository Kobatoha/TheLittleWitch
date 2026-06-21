from sqladmin import ModelView

from app.models import Category, Item, User
from app.models.plant import Plant
from app.models.garden_bed import GardenBed


class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"

    column_list = [User.id, User.username, User.email, User.is_active, User.created_at]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username, User.created_at]
    form_columns = [User.username, User.email, User.is_active]


class CategoryAdmin(ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"
    icon = "fa-solid fa-folder"

    column_list = [Category.id, Category.name, Category.description]
    column_searchable_list = [Category.name]
    form_columns = [Category.name, Category.description]


class ItemAdmin(ModelView, model=Item):
    name = "Предмет"
    name_plural = "Предметы"
    icon = "fa-solid fa-box"

    column_list = [
        Item.id,
        Item.name,
        Item.item_type,
        Item.rarity,
        Item.potency_boost,
    ]
    column_searchable_list = [Item.name]
    column_sortable_list = [Item.id, Item.name, Item.item_type, Item.rarity]
    form_columns = [
        Item.name,
        Item.item_type,
        Item.rarity,
        Item.description,
        Item.potency_boost,
        Item.icon,
    ]

class PlantAdmin(ModelView, model=Plant):
    column_list = [
        Plant.id,
        Plant.name,
        Plant.base_vitality,
        Plant.essence_per_care,
        Plant.growth_per_care,
        Plant.min_harvest_stage,
    ]
    column_searchable_list = [Plant.name]
    column_sortable_list = [Plant.id, Plant.name, Plant.base_vitality, Plant.growth_per_care]
    form_columns = [
        Plant.name,
        Plant.description,
        Plant.icon,
        Plant.base_vitality,
        Plant.vitality_decay,
        Plant.essence_per_care,
        Plant.growth_per_care,
        Plant.min_harvest_stage,
        Plant.base_potency,
    ]
    name = "Растение"
    name_plural = "Растения"

class GardenBedAdmin(ModelView, model=GardenBed):
    column_list = [
        GardenBed.id,
        GardenBed.player_id,
        GardenBed.plant_id,
        GardenBed.growth_stage,
        GardenBed.vitality,
        GardenBed.essence,
        GardenBed.planted_at,
    ]
    column_sortable_list = [
        GardenBed.id,
        GardenBed.growth_stage,
        GardenBed.vitality,
        GardenBed.planted_at,
    ]
    name = "Грядка"
    name_plural = "Грядки"

