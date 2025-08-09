from panda3d.core import *
from panda3d.bullet import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Point3
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TransparencyAttrib
import sys
import random
import math





class DroppedItem:
    def __init__(self, base, block_type, pos, texture, model):
        self.block_type = block_type

        shape = BulletBoxShape(Vec3(0.3, 0.3, 0.3))
        self.node = BulletRigidBodyNode("dropped_item")
        self.node.addShape(shape)
        self.node.setMass(1.0)
        self.node.setPythonTag("dropped_item", self)

        self.np = render.attachNewNode(self.node)
        self.np.setPos(pos)
        base.physics_world.attachRigidBody(self.node)

        self.model = model.copyTo(self.np)
        self.model.setTexture(texture)
        self.model.setScale(0.5)

    def pickup(self, base):
        base.physics_world.removeRigidBody(self.node)
        self.np.removeNode()

class MinecraftSimple(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()

        self.selected_block = "grass"
        self.speed = 5
        self.gravity = -20
        self.jump_speed = 7

        self.is_crouching = False
        self.normal_speed = self.speed
        self.crouch_speed = self.speed * 0.2

        

        self.textures = {
            "grass": self.loader.loadTexture("assets/textures/groundEarth.png"),
            "dirt": self.loader.loadTexture("assets/textures/groundMud.png"),
            "stone": self.loader.loadTexture("assets/textures/wallStone.png"),
            "bedrock": self.loader.loadTexture("assets/textures/stone07.png"),
            "leafs": self.loader.loadTexture("assets/textures/wallBrick06.png"),
            "chest": self.loader.loadTexture("assets/textures/wallBrick05.png"),
        }

        self.model = self.loader.loadModel("assets/models/block_model.obj")

        self.inventory = {}
        self.dropped_items = []

        #self.pigs = []
        #self.spawn_pig((7, 7, 1))
        
        self.slot_keys = ["grass", "dirt", "stone"]

        self.chests = []  # список усіх сундуків
        self.opened_chest = None  # поточний відкритий сундук
        self.chest_ui_text = None

        self.accept("e", self.try_open_chest)

        self.hotbar_slots = {}
        self.hotbar_texts = {}

        self.accept("escape", sys.exit)
        self.accept("mouse1", self.place_block)
        self.accept("mouse3", self.remove_block)
        self.accept("space", self.jump)
        self.accept("control", self.start_crouch)
        self.accept("control-up", self.stop_crouch)
        self.accept("i", self.print_inventory)

        self.accept("1", self.set_block_type, ["grass"])
        self.accept("2", self.set_block_type, ["dirt"])
        self.accept("3", self.set_block_type, ["stone"])

        self.setup_physics()
        self.create_player()
        self.create_flat_world()
        self.create_treee((10, 10, 1))
        self.create_chest((5, 5, 1))

        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)

        self.init_hotbar()
        self.center_mouse()
        self.taskMgr.add(self.update, "update")

    def setup_physics(self):
        self.physics_world = BulletWorld()
        self.physics_world.setGravity(Vec3(0, 0, self.gravity))

    def create_player(self):
        shape = BulletCapsuleShape(0.4, 1.0, ZUp)
        self.player_node = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.player_node.setGravity(-self.gravity)
        self.player_node.setJumpSpeed(self.jump_speed)
        self.player_node.setMaxJumpHeight(2.0)

        self.player_np = render.attachNewNode(self.player_node)
        self.player_np.setPos(1, 5, 8)
        self.physics_world.attachCharacter(self.player_node)

        self.camera.reparentTo(self.player_np)
        self.camera.setZ(1.6)

    def create_flat_world(self):
        for z in range(4):
            for x in range(20):
                for y in range(20):
                    self.create_block(LPoint3(x, y, -z), "grass" if z == 0 else "dirt")

    def create_treee(self, base_pos):
        x0, y0, z0 = base_pos
        for i in range(4):
            self.create_block(LPoint3(x0, y0, z0 + i), "dirt")
        for z in range(3):
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if x == 0 and y == 0 and z == 0:
                        continue
                    self.create_block(LPoint3(x0 + x, y0 + y, z0 + 3 + z), "leafs")

    #def get_terrain_height(self, x, y):
        #x, y = round(x), round(y)
        #for z in range(10, -1, -1):
            #result = self.physics_world.rayTestClosest(Point3(x, y, z + 0.5), Point3(x, y, z - 2))
            #if result.hasHit():
                #return result.getHitPos().z + 0.5
        #return 0

    def create_block(self, pos, block_type):
        shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))
        node = BulletRigidBodyNode("block")
        node.addShape(shape)
        node.setMass(0)
        node.setPythonTag("block_type", block_type)
        np = render.attachNewNode(node)
        np.setPos(pos)
        np.setHpr(0, 90, 0)
        self.physics_world.attachRigidBody(node)

        block = self.model.copyTo(np)
        block.setTexture(self.textures[block_type])
        node.setPythonTag("block_nodepath", np)
        return np

    def place_block(self):
        if base.mouseWatcherNode.hasMouse():
            if self.selected_block not in self.inventory or self.inventory[self.selected_block] <= 0:
                print(f"❌ Немає {self.selected_block} в інвентарі!")
                return

            from_pos = self.camera.getPos(render)
            to_pos = from_pos + self.camera.getQuat(render).getForward() * 5
            result = self.physics_world.rayTestClosest(from_pos, to_pos)

            if result.hasHit():
                hit_pos = result.getHitPos()
                normal = result.getHitNormal()
                pos = hit_pos + normal * 0.5
                pos = LPoint3(round(pos.x), round(pos.y), round(pos.z))
                self.create_block(pos, self.selected_block)

                self.inventory[self.selected_block] -= 1
                if self.inventory[self.selected_block] <= 0:
                    del self.inventory[self.selected_block]

                print(f"📦 Поставлено {self.selected_block}, залишилось: {self.inventory.get(self.selected_block, 0)}")
                self.update_hotbar()

    def remove_block(self):
        if base.mouseWatcherNode.hasMouse():
            from_pos = self.camera.getPos(render)
            to_pos = from_pos + self.camera.getQuat(render).getForward() * 5

            result = self.physics_world.rayTestClosest(from_pos, to_pos)
            if result.hasHit():
                node = result.getNode()
                block_type = node.getPythonTag("block_type") if node.hasPythonTag("block_type") else None

                if block_type != "bedrock":
                    block_np = node.getPythonTag("block_nodepath")
                    if block_np:
                        drop_pos = block_np.getPos() + Vec3(0, 0, 0.5)
                        item = DroppedItem(self, block_type, drop_pos, self.textures[block_type], self.model)
                        self.dropped_items.append(item)

                        self.physics_world.removeRigidBody(node)
                        block_np.removeNode()

                        if block_type == "chest":
                            chest_inventory = node.getPythonTag("chest_inventory")
                            for item, count in chest_inventory.items():
                                for i in range(count):
                                    self.spawn_item(item, block_np.getPos(render))
                            chest_inventory.clear()

                        else:
                            # Для звичайних блоків — просто додаємо до інвентаря
                            self.inventory[block_type] = self.inventory.get(block_type, 0) + 1
                            self.update_hotbar()

                        block_np.removeNode()

                        print(f"🪙 {block_type} впав на землю.")

    def check_item_pickup(self):
        player_pos = self.player_np.getPos()
        collected = []

        for item in self.dropped_items:
            dist = (item.np.getPos() - player_pos).length()
            if dist < 1.0:
                item.pickup(self)
                self.inventory[item.block_type] = self.inventory.get(item.block_type, 0) + 1
                collected.append(item)
                print(f"📥 Підібрано {item.block_type}")
        
        for item in collected:
            self.dropped_items.remove(item)
            self.update_hotbar()

    def set_block_type(self, block_type):
        self.selected_block = block_type
        print(f"✅ Вибрано блок: {block_type}")
        self.update_hotbar()

    def create_chest(self, pos):
        chest_np = self.create_block(pos, "stone")  # Використаємо "stone" як базову текстуру

        chest_node = chest_np.node()
        chest_node.setPythonTag("block_type", "chest")
        chest_node.setPythonTag("block_nodepath", chest_np)
        chest_node.setPythonTag("chest_inventory", {"dirt": 3, "stone": 5})  # приклад вмісту

        self.chests.append(chest_node)

    def try_open_chest(self):
        if base.mouseWatcherNode.hasMouse():
            from_pos = self.camera.getPos(render)
            to_pos = from_pos + self.camera.getQuat(render).getForward() * 3
            result = self.physics_world.rayTestClosest(from_pos, to_pos)

            if result.hasHit():
                node = result.getNode()
                if node.hasPythonTag("block_type") and node.getPythonTag("block_type") == "chest":
                    chest_inventory = node.getPythonTag("chest_inventory")
                    self.opened_chest = node
                    self.show_chest_inventory(chest_inventory)

        
        

    def spawn_item(self, block_type, pos):
        model = self.create_block(pos + Vec3(0, 0, 0.5), block_type)
        model.setScale(0.3)
        model.setTag("pickup", "1")
        model.setTag("type", block_type)
        self.dropped_items.append(model)

    def show_chest_inventory(self, chest_inventory):
        if self.chest_ui_text:
            self.chest_ui_text.destroy()

        text = "🧰 Сундук відкрито:\n"
        for item, count in chest_inventory.items():
            text += f"- {item}: {count}\n"

        text += "\nНатисни [T], щоб взяти всі предмети."

        self.chest_ui_text = OnscreenText(text=text, pos=(0, 0.3), scale=0.05, fg=(1, 1, 1, 1), mayChange=True)
        self.accept("t", self.take_from_chest)

    def take_from_chest(self):
        if self.opened_chest:
            chest_inventory = self.opened_chest.getPythonTag("chest_inventory")
            for item, count in chest_inventory.items():
                self.inventory[item] = self.inventory.get(item, 0) + count
            chest_inventory.clear()

            if self.chest_ui_text:
                self.chest_ui_text.destroy()
                self.chest_ui_text = None

            self.opened_chest = None
            print("📥 Всі речі перенесено в інвентар.")
            self.update_hotbar()

    def print_inventory(self):
        print("📦 Інвентар:")
        if not self.inventory:
            print("  (порожній)")
        else:
            for block, count in self.inventory.items():
                marker = " <- [вибрано]" if block == self.selected_block else ""
                print(f"  {block}: {count}{marker}")

    def init_hotbar(self):
        for i, block_type in enumerate(self.slot_keys):
            x = -0.3 + i * 0.3
            image = OnscreenImage(image="assets/textures/ui/" + block_type + "_icon.png",
                                  pos=(x, 0, -0.9),
                                  scale=(0.1, 1, 0.1))
            image.setTransparency(TransparencyAttrib.MAlpha)
            self.hotbar_slots[block_type] = image

            count_text = OnscreenText(text="", pos=(x, -0.99), scale=0.05,
                                      fg=(1, 1, 1, 1), mayChange=True)
            self.hotbar_texts[block_type] = count_text

        self.update_hotbar()

    def update_hotbar(self):
        for block_type, img in self.hotbar_slots.items():
            if block_type == self.selected_block:
                img.setScale(0.12, 1, 0.12)
            else:
                img.setScale(0.1, 1, 0.1)
            count = self.inventory.get(block_type, 0)
            self.hotbar_texts[block_type].setText(str(count) if count > 0 else "")

    def jump(self):
        if self.player_node.canJump():
            self.player_node.doJump()

    #def spawn_pig(self, pos):
        #pig = Pig(self, pos)
        #self.pigs.append(pig)

    def update(self, task):
        dt = globalClock.getDt()
        self.physics_world.doPhysics(dt, 5, 1.0 / 180.0)
        self.handle_movement(dt)
        self.handle_camera()
        self.check_item_pickup()
        #for pig in self.pigs:
            #pig.update(dt)
        return Task.cont

    def handle_movement(self, dt):
        move_dir = Vec3(0, 0, 0)
        if self.mouseWatcherNode.is_button_down(KeyboardButton.ascii_key('w')):
            move_dir.y += 1
        if self.mouseWatcherNode.is_button_down(KeyboardButton.ascii_key('s')):
            move_dir.y -= 1
        if self.mouseWatcherNode.is_button_down(KeyboardButton.ascii_key('a')):
            move_dir.x -= 1
        if self.mouseWatcherNode.is_button_down(KeyboardButton.ascii_key('d')):
            move_dir.x += 1

        if move_dir.length() > 0:
            move_dir.normalize()
            move_dir *= self.speed
            quat = Quat()
            quat.setHpr((self.player_np.getH(), 0, 0))
            global_move = quat.xform(move_dir * dt)
            next_pos = self.player_np.getPos() + Vec3(global_move.x, global_move.y, 0)
            block_x = round(self.player_np.getX())
            block_y = round(self.player_np.getY())
            if self.is_crouching:
                if not (block_x - 0.4 <= next_pos.x <= block_x + 0.4 and
                        block_y - 0.4 <= next_pos.y <= block_y + 0.4):
                    move_dir = Vec3(0, 0, 0)

        self.player_node.setLinearMovement(move_dir, True)

    def start_crouch(self):
        if self.is_crouching:
            return
        self.is_crouching = True
        self.speed = self.crouch_speed

        pos = self.player_np.getPos()
        hpr = self.player_np.getHpr()
        self.physics_world.removeCharacter(self.player_node)
        self.player_np.detachNode()

        shape = BulletCapsuleShape(0.4, 0.5, ZUp)
        self.player_node = BulletCharacterControllerNode(shape, 0.4, 'PlayerCrouch')
        self.player_np = render.attachNewNode(self.player_node)
        self.player_np.setPos(pos)
        self.player_np.setHpr(hpr)
        self.physics_world.attachCharacter(self.player_node)

        self.camera.reparentTo(self.player_np)
        self.camera.setZ(1.0)

    def stop_crouch(self):
        if not self.is_crouching:
            return
        self.is_crouching = False
        self.speed = self.normal_speed

        pos = self.player_np.getPos()
        hpr = self.player_np.getHpr()
        self.physics_world.removeCharacter(self.player_node)
        self.player_np.detachNode()

        shape = BulletCapsuleShape(0.4, 1.0, ZUp)
        self.player_node = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.player_np = render.attachNewNode(self.player_node)
        self.player_np.setPos(pos)
        self.player_np.setHpr(hpr)
        self.physics_world.attachCharacter(self.player_node)

        self.camera.reparentTo(self.player_np)
        self.camera.setZ(1.6)

    def handle_camera(self):
        center_x = self.win.getXSize() // 2
        center_y = self.win.getYSize() // 2
        md = self.win.getPointer(0)
        x = md.getX()
        y = md.getY()

        delta_x = x - center_x
        delta_y = y - center_y

        sensitivity = 0.2
        self.player_np.setH(self.player_np.getH() - delta_x * sensitivity)

        pitch = self.camera.getP() - delta_y * sensitivity
        pitch = max(-90, min(90, pitch))
        self.camera.setP(pitch)

        self.center_mouse()

    def center_mouse(self):
        center_x = self.win.getXSize() // 2
        center_y = self.win.getYSize() // 2
        self.win.movePointer(0, center_x, center_y)


MinecraftSimple().run()