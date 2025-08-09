#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft-подібна гра на Panda3D з правильною AABB колізією, стрибками та текстурами
Встановлення: pip install panda3d
Запуск: python minecraft_game.py

Керування:
- WASD: рух
- Space: стрибок
- Миша: огляд
- ЛКМ: руйнування блоку
- ПКМ: розміщення блоку
- 1,2,3: переключення типу блоку
- ESC: повернення в меню
"""

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import *
import sys
import math
import os

class MinecraftGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Приховати повідомлення про графічний пайп
        self.notify.setDebug(False)
        
        # Повноекранний режим або великий розмір вікна
        props = WindowProperties()
        props.setSize(1920, 1080)  # Full HD розмір
        props.setTitle("Minecraft Game")
        self.win.requestProperties(props)
        
        # Налаштування вікна
        self.setBackgroundColor(0.5, 0.8, 1.0)  # Блакитне небо
        
        # Ініціалізація змінних
        self.world = {}  # Словник для зберігання блоків
        self.selected_block = 0  # Поточний тип блоку
        self.block_types = ['grass', 'stone', 'wood']
        self.block_names = ['Grass', 'Stone', 'Wood']
        
        # Завантаження текстур
        self.load_textures()
        
        # Стан гри
        self.game_state = "menu"
        
        # Змінні для камери
        self.camera_h = 0  # Горизонтальний поворот
        self.camera_p = 0  # Вертикальний поворот
        
        # Розмір гравця - 2 блоки висотою (як у першому коді)
        # Позиція гравця (центр його AABB)
        self.player_pos = Vec3(0.5, -4.5, 2.0)  # В центрі блоку, вище платформи
        
        # Швидкість гравця
        self.velocity = Vec3(0, 0, 0)
        
        # Параметри гравця (AABB розміри)
        self.player_width = 0.6   # Ширина гравця (менше блоку)
        self.player_height = 1.5  # Висота гравця рівно 2 блоки
        
        # Фізичні константи
        self.gravity = 20.0
        self.jump_speed = 8.0
        self.max_fall_speed = 20.0
        self.move_speed = 4.0
        
        # Стан на землі
        self.on_ground = False
        
        # Змінні для керування мишею
        self.mouse_sensitivity = 0.2
        self.mouse_enabled = False
        
        # Підсвічування блоків
        self.highlighted_block = None
        self.highlight_node = None
        
        # Створення меню
        self.create_menu()
        
        # Налаштування освітлення
        self.setup_lighting()
        
    def load_textures(self):
        """Завантаження текстур для блоків"""
        # Спроба завантажити текстури
        self.grass_texture = self.loader.loadTexture("grass.png")
        self.stone_texture = self.loader.loadTexture("stone.png")
        self.wood_texture = self.loader.loadTexture("wood.png")
            
        # Налаштування фільтрації текстур
        for tex in [self.grass_texture, self.stone_texture, self.wood_texture]:
            if tex:
                tex.setMinfilter(Texture.FTLinearMipmapLinear)
                tex.setMagfilter(Texture.FTLinear)
                
        self.block_textures = [
            self.grass_texture,
            self.stone_texture,
            self.wood_texture
        ]
        self.block_colors = None  # Використовуємо текстури замість кольорів
        
    def setup_lighting(self):
        # Направлене освітлення (сонце)
        dlight = DirectionalLight('dlight')
        dlight.setDirection(Vec3(-1, -1, -1))
        dlight.setColor((1, 1, 0.9, 1))
        dlnp = self.render.attachNewNode(dlight)
        self.render.setLight(dlnp)
        
        # Загальне освітлення
        alight = AmbientLight('alight')
        alight.setColor((0.3, 0.3, 0.4, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
    def create_menu(self):
        # Очищення попереднього меню
        if hasattr(self, 'menu_items'):
            for item in self.menu_items:
                item.destroy()
        
        self.menu_items = []
        
        # Заголовок
        title = OnscreenText(
            text="MINECRAFT GAME",
            pos=(0, 0.5),
            scale=0.15,
            fg=(1, 1, 1, 1),
            shadow=(0.5, 0.5, 0.5, 1)
        )
        self.menu_items.append(title)
        
        # Кнопка "Грати"
        play_btn = DirectButton(
            text="PLAY",
            scale=0.1,
            pos=(0, 0, 0.1),
            command=self.start_game,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.2, 0.7, 0.2, 0.8),
            frameSize=(-2, 2, -0.5, 0.5)
        )
        self.menu_items.append(play_btn)
        
        # Кнопка "Вихід"
        exit_btn = DirectButton(
            text="EXIT",
            scale=0.1,
            pos=(0, 0, -0.1),
            command=self.exit_game,
            text_fg=(1, 1, 1, 1),
            frameColor=(0.7, 0.2, 0.2, 0.8),
            frameSize=(-2, 2, -0.5, 0.5)
        )
        self.menu_items.append(exit_btn)
        
    def start_game(self):
        # Приховати меню
        for item in self.menu_items:
            item.hide()
            
        self.game_state = "game"
        
        # Налаштувати камеру
        self.setup_camera()
        
        # Створити світ
        self.create_world()
        
        # Налаштувати керування
        self.setup_controls()
        
        # Налаштувати UI гри
        self.setup_game_ui()
        
        # Увімкнути керування мишею
        self.enable_mouse_control()
        
    def setup_camera(self):
        """Налаштування камери"""
        # Скинути стан
        self.camera_h = 0
        self.camera_p = 0
        self.player_pos = Vec3(0.5, -4.5, 3.0)  # Безпечна позиція над платформою
        self.velocity = Vec3(0, 0, 0)
        self.on_ground = False
        
        # Встановити позицію камери (очі гравця - трохи вище центру)
        eye_height = self.player_height * 0.85  # Очі близько до верху голови
        camera_pos = Vec3(self.player_pos.x, self.player_pos.y, self.player_pos.z + eye_height)
        
        self.camera.setPos(camera_pos)
        self.camera.setHpr(self.camera_h, self.camera_p, 0)
        
        # Видалити стандартне керування камерою
        self.disableMouse()
        
        # Налаштування near/far клipping для кращої видимості
        lens = self.cam.node().getLens()
        lens.setNear(0.01)  # Дуже близько до камери
        lens.setFar(1000.0)  # Далеко
        
    def create_world(self):
        # Створити базову платформу 20x20
        for x in range(-10, 10):
            for z in range(-10, 10):
                self.place_block(x, 0, z, 0)  # трава на рівні 0
                self.place_block(x, -1, z, 1)  # камінь під нею
                
        # Додати кілька блоків для тестування
        self.place_block(0, 1, 0, 2)   # дерево
        self.place_block(1, 1, 0, 2)   # дерево
        self.place_block(0, 1, 1, 2)   # дерево
        
        # Створити невелику структуру
        for i in range(3):
            self.place_block(5, i+1, 0, 1)  # драбина з каменю
            
        self.place_block(-2, 1, -2, 1)  # камінь
        self.place_block(-2, 2, -2, 1)  # камінь
        
        # Створити рамку для підсвічування
        self.create_highlight_box()
            
    def place_block(self, x, y, z, block_type):
        """Розмістити блок у світі"""
        # Створити куб
        geom_node = self.create_cube_geometry()
        block = self.render.attachNewNode(geom_node)
        
        # Позиція блоку: центр блоку в координатах (x+0.5, z+0.5, y+0.5)
        # Конвертація: блокові координати (x,y,z) -> Panda3D (x+0.5, z+0.5, y+0.5)
        block.setPos(x + 0.5, z + 0.5, y + 0.5)
        block.setScale(0.5, 0.5, 0.5)
        
        # Застосувати текстуру
        if self.block_textures and block_type < len(self.block_textures) and self.block_textures[block_type]:
            ts = TextureStage('ts')
            block.setTexture(ts, self.block_textures[block_type])
        
        # Зберегти в світі
        self.world[(x, y, z)] = {
            'node': block,
            'type': block_type
        }
        
    def create_cube_geometry(self):
        """Створити геометрію куба"""
        format = GeomVertexFormat.getV3n3t2()
        vdata = GeomVertexData('cube', format, Geom.UHStatic)
        vdata.setNumRows(24)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        texcoord = GeomVertexWriter(vdata, 'texcoord')
        
        # Вершини куба з нормалями та текстурними координатами
        faces = [
            # Передня грань (Z+)
            [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1), (0, 0, 1)],
            # Задня грань (Z-)
            [(1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1), (0, 0, -1)],
            # Права грань (X+)
            [(1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1), (1, 0, 0)],
            # Ліва грань (X-)
            [(-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, 0, 0)],
            # Верхня грань (Y+)
            [(-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1), (0, 1, 0)],
            # Нижня грань (Y-)
            [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1), (0, -1, 0)]
        ]
        
        tex_coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
        
        for face in faces:
            for i in range(4):
                vertex.addData3f(*face[i])
                normal.addData3f(*face[4])
                texcoord.addData2f(*tex_coords[i])
        
        geom = Geom(vdata)
        
        # Додати трикутники
        for i in range(6):
            face_start = i * 4
            prim = GeomTriangles(Geom.UHStatic)
            prim.addVertices(face_start, face_start + 1, face_start + 2)
            prim.addVertices(face_start, face_start + 2, face_start + 3)
            prim.closePrimitive()
            geom.addPrimitive(prim)
            
        geom_node = GeomNode('cube')
        geom_node.addGeom(geom)
        return geom_node
        
    def create_highlight_box(self):
        """Створити рамку для підсвічування блоків"""
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('highlight', format, Geom.UHStatic)
        vdata.setNumRows(8)
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        # Вершини куба
        size = 0.51
        vertex.addData3f(-size, -size, -size)
        vertex.addData3f(size, -size, -size)
        vertex.addData3f(size, size, -size)
        vertex.addData3f(-size, size, -size)
        vertex.addData3f(-size, -size, size)
        vertex.addData3f(size, -size, size)
        vertex.addData3f(size, size, size)
        vertex.addData3f(-size, size, size)
        
        geom = Geom(vdata)
        lines = GeomLines(Geom.UHStatic)
        
        # Ребра куба
        edges = [
            (0,1), (1,2), (2,3), (3,0),  # нижня грань
            (4,5), (5,6), (6,7), (7,4),  # верхня грань
            (0,4), (1,5), (2,6), (3,7)   # вертикальні ребра
        ]
        
        for edge in edges:
            lines.addVertices(edge[0], edge[1])
        lines.closePrimitive()
        geom.addPrimitive(lines)
        
        highlight_geom = GeomNode('highlight')
        highlight_geom.addGeom(geom)
        self.highlight_node = self.render.attachNewNode(highlight_geom)
        
        self.highlight_node.setColor(1, 1, 0, 1)
        self.highlight_node.setRenderModeWireframe()
        self.highlight_node.setRenderModeThickness(3)
        self.highlight_node.hide()
        
    def setup_controls(self):
        """Налаштувати керування"""
        self.keys = {
            'w': False, 's': False, 'a': False, 'd': False, 'space': False
        }
        
        # Прив'язка клавіш
        self.accept("w", self.set_key, ["w", True])
        self.accept("w-up", self.set_key, ["w", False])
        self.accept("s", self.set_key, ["s", True])
        self.accept("s-up", self.set_key, ["s", False])
        self.accept("a", self.set_key, ["a", True])
        self.accept("a-up", self.set_key, ["a", False])
        self.accept("d", self.set_key, ["d", True])
        self.accept("d-up", self.set_key, ["d", False])
        self.accept("space", self.set_key, ["space", True])
        self.accept("space-up", self.set_key, ["space", False])
        
        # Миша
        self.accept("mouse1", self.on_mouse_click, ["destroy"])
        self.accept("mouse3", self.on_mouse_click, ["place"])
        
        # Переключення блоків
        self.accept("1", self.select_block, [0])
        self.accept("2", self.select_block, [1])
        self.accept("3", self.select_block, [2])
        
        # Повернення в меню
        self.accept("escape", self.return_to_menu)
        
        # Запустити завдання оновлення
        self.taskMgr.add(self.update_task, "update-task")
        
    def set_key(self, key, value):
        self.keys[key] = value
        
    def enable_mouse_control(self):
        """Увімкнути керування мишею"""
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)
        self.mouse_enabled = True
        
    def disable_mouse_control(self):
        """Вимкнути керування мишею"""
        props = WindowProperties()
        props.setCursorHidden(False)
        props.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(props)
        self.mouse_enabled = False
        
    def update_task(self, task):
        """Головне завдання оновлення"""
        if self.game_state != "game":
            return task.cont
            
        dt = globalClock.getDt()
        if dt > 0.1:  # Обмежити максимальний dt
            dt = 0.1
            
        # Оновити фізику та рух
        self.update_physics(dt)
        
        # Оновити камеру (включаючи mouse look)
        self.update_camera()
        
        # Оновити підсвічування
        self.update_block_highlight()
        
        return task.cont
        
    def update_physics(self, dt):
        """Система фізики з AABB колізією (з першого коду)"""
        
        # Обробити стрибок
        if self.keys['space'] and self.on_ground:
            self.velocity.z = self.jump_speed
            self.on_ground = False
        
        # Застосувати гравітацію
        if not self.on_ground:
            self.velocity.z -= self.gravity * dt
            if self.velocity.z < -self.max_fall_speed:
                self.velocity.z = -self.max_fall_speed
        
        # Обчислити горизонтальний рух (як у другому коді - відносно камери)
        self.update_horizontal_movement(dt)
        
        # Застосувати рух з перевіркою колізій
        self.move_with_collision(dt)
        
        # Перевірити чи гравець на землі
        self.check_ground()
        
        # Перевіряти кордони світу
        if self.player_pos.z < -50:
            self.player_pos = Vec3(0.5, -4.5, 3.0)
            self.velocity = Vec3(0, 0, 0)
            self.on_ground = False
            
    def update_horizontal_movement(self, dt):
        """Оновити горизонтальну швидкість відносно камери (з другого коду)"""
        # Використовувати матрицю камери для правильних напрямків
        cam_mat = self.camera.getMat()
        
        # Вектори напрямків камери в світових координатах
        forward = cam_mat.getRow3(1)   # Y це вперед
        right = cam_mat.getRow3(0)     # X це вправо
        forward.setZ(0)  # Ігнорувати вертикальну складову для руху по землі
        right.setZ(0)
        
        # Нормалізувати вектори
        if forward.length() > 0:
            forward.normalize()
        if right.length() > 0:
            right.normalize()
        
        # Скинути горизонтальну швидкість
        self.velocity.x = 0
        self.velocity.y = 0
        
        # Застосувати рух залежно від натиснутих клавіш
        move_vec = Vec3(0, 0, 0)
        if self.keys['w']:  # Вперед відносно камери
            move_vec += forward
        if self.keys['s']:  # Назад відносно камери
            move_vec -= forward
        if self.keys['a']:  # Вліво відносно камери
            move_vec -= right
        if self.keys['d']:  # Вправо відносно камери
            move_vec += right
            
        # Нормалізувати та застосувати швидкість
        if move_vec.length() > 0:
            move_vec.normalize()
            self.velocity.x = move_vec.x * self.move_speed
            self.velocity.y = move_vec.y * self.move_speed
            
    def move_with_collision(self, dt):
        """Рух з перевіркою колізій по кожній осі окремо (з першого коду)"""
        # Зберегти стару позицію
        old_pos = Vec3(self.player_pos)
        
        # Спробувати рух по X
        new_pos = Vec3(old_pos)
        new_pos.x += self.velocity.x * dt
        if not self.check_aabb_collision(new_pos):
            self.player_pos.x = new_pos.x
        else:
            self.velocity.x = 0
            
        # Спробувати рух по Y
        new_pos = Vec3(self.player_pos)
        new_pos.y += self.velocity.y * dt
        if not self.check_aabb_collision(new_pos):
            self.player_pos.y = new_pos.y
        else:
            self.velocity.y = 0
            
        # Спробувати рух по Z (висота)
        new_pos = Vec3(self.player_pos)
        new_pos.z += self.velocity.z * dt
        
        if not self.check_aabb_collision(new_pos):
            self.player_pos.z = new_pos.z
            self.on_ground = False
        else:
            if self.velocity.z < 0:  # Падіння - приземлення
                # Точно встановити на поверхню
                ground_y = self.find_ground_level(self.player_pos.x, self.player_pos.y)
                if ground_y is not None:
                    self.player_pos.z = ground_y + self.player_height / 2
                    self.on_ground = True
            self.velocity.z = 0
            
    def check_aabb_collision(self, player_center):
        """Перевірити AABB колізію гравця з блоками (з першого коду)"""
        # AABB гравця
        half_width = self.player_width / 2
        half_height = self.player_height / 2
        
        player_min = Vec3(
            player_center.x - half_width,
            player_center.y - half_width,
            player_center.z - half_height
        )
        player_max = Vec3(
            player_center.x + half_width,
            player_center.y + half_width,
            player_center.z + half_height
        )
        
        # Знайти діапазон блоків для перевірки
        min_block_x = int(math.floor(player_min.x))
        max_block_x = int(math.floor(player_max.x))
        min_block_y = int(math.floor(player_min.z))  # Z гравця = Y блоку
        max_block_y = int(math.floor(player_max.z))
        min_block_z = int(math.floor(player_min.y))  # Y гравця = Z блоку
        max_block_z = int(math.floor(player_max.y))
        
        # Перевірити кожен блок в діапазоні
        for bx in range(min_block_x, max_block_x + 1):
            for by in range(min_block_y, max_block_y + 1):
                for bz in range(min_block_z, max_block_z + 1):
                    if (bx, by, bz) in self.world:
                        # AABB блоку (блок розміром 1x1x1 з центром в (bx+0.5, by+0.5, bz+0.5))
                        block_min = Vec3(bx, bz, by)  # Конвертація координат
                        block_max = Vec3(bx + 1, bz + 1, by + 1)
                        
                        # Перевірити перетин AABB
                        if (player_min.x < block_max.x and player_max.x > block_min.x and
                            player_min.y < block_max.y and player_max.y > block_min.y and
                            player_min.z < block_max.z and player_max.z > block_min.z):
                            return True
        return False
        
    def find_ground_level(self, x, y):
        """Знайти рівень землі під гравцем (з першого коду)"""
        block_x = int(math.floor(x))
        block_z = int(math.floor(y))
        
        # Шукати найвищий блок під гравцем
        for block_y in range(int(self.player_pos.z), -50, -1):
            if (block_x, block_y, block_z) in self.world:
                return block_y + 1  # Поверхня блоку
        return None
        
    def check_ground(self):
        """Перевірити чи гравець на землі (з першого коду)"""
        # Перевірити позицію трохи нижче
        test_pos = Vec3(self.player_pos)
        test_pos.z -= 0.01
        
        self.on_ground = self.check_aabb_collision(test_pos)
        
    def update_camera(self):
        """Оновити позицію та поворот камери (комбінація з обох кодів)"""
        # Оновити поворот миші (з другого коду)
        if self.mouse_enabled and self.mouseWatcherNode.hasMouse():
            mouse_x = self.mouseWatcherNode.getMouseX()
            mouse_y = self.mouseWatcherNode.getMouseY()
            
            if abs(mouse_x) > 0.001 or abs(mouse_y) > 0.001:
                self.camera_h -= mouse_x * self.mouse_sensitivity * 100
                self.camera_p += mouse_y * self.mouse_sensitivity * 100
                self.camera_p = max(-89, min(89, self.camera_p))
                
                # Центрувати миш
                center_x = self.win.getXSize() // 2
                center_y = self.win.getYSize() // 2
                self.win.movePointer(0, center_x, center_y)
        
        # Оновити позицію камери (очі гравця) - з першого коду
        eye_height = self.player_height * 0.85
        camera_pos = Vec3(
            self.player_pos.x,
            self.player_pos.y,
            self.player_pos.z + eye_height
        )
        
        self.camera.setPos(camera_pos)
        self.camera.setHpr(self.camera_h, self.camera_p, 0)
        
    def update_block_highlight(self):
        """Оновити підсвічування блоків (виправлено)"""
        target_block = self.get_target_block()
        
        if target_block != self.highlighted_block:
            self.highlighted_block = target_block
            
            if target_block:
                x, y, z = target_block
                # Позиція підсвічування (центр блоку)
                self.highlight_node.setPos(x + 0.5, z + 0.5, y + 0.5)
                self.highlight_node.show()
            else:
                self.highlight_node.hide()
                
    def get_target_block(self):
        """Знайти блок, на який дивиться гравець (виправлено для кращої точності)"""
        # Отримати позицію камери та її орієнтацію
        camera_pos = self.camera.getPos()
        
        # Отримати матрицю камери для обчислення напрямку
        camera_mat = self.camera.getMat()
        forward = camera_mat.getRow3(1)  # Напрямок "вперед" камери
        forward.normalize()
        
        # Raycast з меншими кроками для кращої точності
        max_distance = 5.0
        step_size = 0.02  # Дуже маленький крок
        steps = int(max_distance / step_size)
        
        for i in range(1, steps):
            distance = i * step_size
            target_pos = camera_pos + forward * distance
            
            # Конвертувати в координати блоків
            block_x = int(math.floor(target_pos.x))
            block_y = int(math.floor(target_pos.z))  # Z Panda3D -> Y блоку
            block_z = int(math.floor(target_pos.y))  # Y Panda3D -> Z блоку
            
            block_pos = (block_x, block_y, block_z)
            
            if block_pos in self.world:
                return block_pos
                
        return None
        
    def get_target_position_for_placement(self):
        """Знайти позицію для розміщення нового блоку (покращено з точним raycast)"""
        target_block = self.get_target_block()
        if not target_block:
            return None
            
        # Отримати позицію камери та напрямок
        camera_pos = self.camera.getPos()
        camera_mat = self.camera.getMat()
        forward = camera_mat.getRow3(1)
        forward.normalize()
        
        x_block, y_block, z_block = target_block
        
        # Знайти точну точку попадання на блок за допомогою raycast
        block_center_panda = Vec3(x_block + 0.5, z_block + 0.5, y_block + 0.5)
        
        # Raycast до точки попадання в блок
        max_distance = 5.0
        step_size = 0.01
        steps = int(max_distance / step_size)
        
        hit_point = None
        
        for i in range(1, steps):
            distance = i * step_size
            test_pos = camera_pos + forward * distance
            
            # Перевірити чи точка в середині блоку
            if (test_pos.x >= x_block and test_pos.x <= x_block + 1 and
                test_pos.y >= z_block and test_pos.y <= z_block + 1 and
                test_pos.z >= y_block and test_pos.z <= y_block + 1):
                hit_point = test_pos
                break
        
        if not hit_point:
            # Якщо не знайшли точку попадання, використати центр блоку
            hit_point = block_center_panda
        
        # Визначити найближчу грань до точки попадання
        # Відстані до граней блоку
        distances_to_faces = {
            'right':  abs(hit_point.x - (x_block + 1)),  # X+
            'left':   abs(hit_point.x - x_block),        # X-
            'top':    abs(hit_point.z - (y_block + 1)),  # Z+ (Y блоку)
            'bottom': abs(hit_point.z - y_block),        # Z- (Y блоку)
            'front':  abs(hit_point.y - (z_block + 1)),  # Y+ (Z блоку)
            'back':   abs(hit_point.y - z_block),        # Y- (Z блоку)
        }
        
        # Знайти найближчу грань
        closest_face = min(distances_to_faces, key=distances_to_faces.get)
        
        # Визначити позицію для нового блоку
        new_pos = None
        
        if closest_face == 'right':
            new_pos = (x_block + 1, y_block, z_block)
        elif closest_face == 'left':
            new_pos = (x_block - 1, y_block, z_block)
        elif closest_face == 'top':
            new_pos = (x_block, y_block + 1, z_block)
        elif closest_face == 'bottom':
            new_pos = (x_block, y_block - 1, z_block)
        elif closest_face == 'front':
            new_pos = (x_block, y_block, z_block + 1)
        elif closest_face == 'back':
            new_pos = (x_block, y_block, z_block - 1)
        
        # Перевірити чи позиція вільна
        if new_pos and new_pos not in self.world:
            return new_pos
                
        return None
        
    def on_mouse_click(self, action):
        """Обробка кліків миші (виправлено з додаванням діагностики)"""
        if self.game_state != "game":
            return
            
        print(f"Mouse click: {action}")  # Діагностика
        
        if action == "destroy":
            self.handle_block_destroy()
        elif action == "place":
            self.handle_block_place()
            
    def handle_block_destroy(self):
        """Руйнування блоку (додано діагностику)"""
        target_block = self.get_target_block()
        if target_block:
            print(f"Destroying block at {target_block}")
            self.remove_block(*target_block)
        else:
            print("No block to destroy")
            
    def handle_block_place(self):
        """Розміщення блоку з перевіркою колізії з гравцем (виправлено)"""
        target_pos = self.get_target_position_for_placement()
        if target_pos:
            print(f"Trying to place block at {target_pos}")
            
            # Перевірити колізію з гравцем
            # Створити тимчасовий блок для тестування
            temp_world = self.world.copy()
            temp_world[target_pos] = {'node': None, 'type': self.selected_block}
            
            old_world = self.world
            self.world = temp_world
            collision = self.check_aabb_collision(self.player_pos)
            self.world = old_world
            
            if not collision:
                print(f"Placing block at {target_pos}")
                self.place_block(*target_pos, self.selected_block)
            else:
                print(f"Cannot place block at {target_pos} - player collision!")
        else:
            print("No valid position for placement")
                
    def remove_block(self, x, y, z):
        """Видалити блок"""
        if (x, y, z) in self.world:
            self.world[(x, y, z)]['node'].removeNode()
            del self.world[(x, y, z)]
            print(f"Block removed at ({x}, {y}, {z})")
            
    def select_block(self, block_type):
        """Вибрати тип блоку"""
        self.selected_block = block_type
        if hasattr(self, 'block_info'):
            self.block_info.setText(f"Block: {self.block_names[self.selected_block]}")
        print(f"Selected block: {self.block_names[self.selected_block]}")
            
    def setup_game_ui(self):
        """Налаштувати UI гри"""
        # Інформація про поточний блок
        self.block_info = OnscreenText(
            text=f"Block: {self.block_names[self.selected_block]}",
            pos=(-1.3, 0.9),
            scale=0.07,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Інструкції
        instructions = OnscreenText(
            text="WASD: move | Space: jump | Mouse: look | LMB: destroy | RMB: build | 1,2,3: block type | ESC: menu",
            pos=(0, -0.95),
            scale=0.05,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Приціл
        crosshair = OnscreenText(
            text="+",
            pos=(0, 0),
            scale=0.1,
            fg=(1, 1, 0, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Інформація про фізику
        self.physics_info = OnscreenText(
            text="",
            pos=(-1.3, 0.8),
            scale=0.05,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        
        # Діагностична інформація
        self.debug_info = OnscreenText(
            text="",
            pos=(1.0, 0.9),
            scale=0.05,
            fg=(1, 1, 0, 1),
            shadow=(0, 0, 0, 1)
        )
        
        self.game_ui = [self.block_info, instructions, crosshair, self.physics_info, self.debug_info]
        
        # Запустити оновлення UI
        self.taskMgr.add(self.update_ui, "update-ui")
        
    def update_ui(self, task):
        """Оновлення UI (додано діагностику)"""
        if self.game_state != "game":
            return task.cont
            
        # Показати інформацію про фізику
        on_ground_text = "Ground" if self.on_ground else "Air"
        velocity_text = f"Vel: {self.velocity.z:.1f}"
        pos_text = f"Pos: {self.player_pos.x:.1f}, {self.player_pos.y:.1f}, {self.player_pos.z:.1f}"
        
        self.physics_info.setText(f"{on_ground_text} | {velocity_text} | {pos_text}")
        
        # Діагностична інформація з гранню
        target_block = self.get_target_block()
        target_place = self.get_target_position_for_placement()
        
        face_info = ""
        if target_block and target_place:
            # Визначити яку грань ми обрали
            x_diff = target_place[0] - target_block[0]
            y_diff = target_place[1] - target_block[1] 
            z_diff = target_place[2] - target_block[2]
            
            if x_diff == 1:
                face_info = "Face: RIGHT"
            elif x_diff == -1:
                face_info = "Face: LEFT"
            elif y_diff == 1:
                face_info = "Face: TOP"
            elif y_diff == -1:
                face_info = "Face: BOTTOM"
            elif z_diff == 1:
                face_info = "Face: FRONT"
            elif z_diff == -1:
                face_info = "Face: BACK"
        
        debug_text = f"Target: {target_block}\nPlace: {target_place}\n{face_info}"
        self.debug_info.setText(debug_text)
        
        return task.cont
        
    def return_to_menu(self):
        """Повернутися в меню"""
        if self.game_state == "game":
            # Очистити світ
            for block_data in self.world.values():
                block_data['node'].removeNode()
            self.world.clear()
            
            # Видалити підсвічування
            if self.highlight_node:
                self.highlight_node.removeNode()
                self.highlight_node = None
            
            # Приховати UI гри
            if hasattr(self, 'game_ui'):
                for ui_item in self.game_ui:
                    ui_item.destroy()
                    
            # Вимкнути керування мишею
            self.disable_mouse_control()
            
            # Зупинити завдання
            self.taskMgr.remove("update-task")
            if self.taskMgr.hasTaskNamed("update-ui"):
                self.taskMgr.remove("update-ui")
            
            # Скинути змінні
            self.highlighted_block = None
            self.velocity = Vec3(0, 0, 0)
            self.on_ground = False
            
            # Повернути стандартне керування камерою для меню
            self.enableMouse()
            
            # Показати меню
            self.game_state = "menu"
            self.create_menu()
            
    def exit_game(self):
        sys.exit()

if __name__ == "__main__":
    game = MinecraftGame()
    game.run()