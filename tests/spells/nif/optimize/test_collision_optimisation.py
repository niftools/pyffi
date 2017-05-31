from tests.scripts.nif import call_niftoaster
import os
import shutil

from . import BaseFileTestCase
from tests import test_logger
import nose
import pyffi
from pyffi.spells import Toaster
from pyffi.formats.nif import NifFormat


class TestCollisionOptimisation(BaseFileTestCase):

    def setUp(self):
        super(TestCollisionOptimisation, self).setUp()
        self.src_name = "test_opt_collision_to_boxshape.nif"
        self.src_file = os.path.join(self.input_files, self.src_name)
        self.dest_file = os.path.join(self.out, self.src_name)
        shutil.copyfile(self.src_file, self.dest_file)
        assert os.path.exists(self.dest_file)

    def test_box_optimisation(self):
        data = NifFormat.Data()
        stream = open(self.src_file, "rb")
        data.read(stream)
        # check initial data
        shape = data.roots[0].collision_object.body.shape
        nose.tools.assert_equals(shape.data.num_vertices, 8)
        sub_shape = shape.sub_shapes[0]
        nose.tools.assert_equals(sub_shape.num_vertices, 8)
        nose.tools.assert_equals(sub_shape.material.material, 0)

        # run the spell that optimizes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=data)
        spell.recurse()
        """
        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [Scene Root] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        optimized box collision
        # pyffi.toaster:INFO:    ~~~ NiNode [Door] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [Door] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [Door] ~~~
        # pyffi.toaster:INFO:    ~~~ NiNode [WoodBeam01] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [WoodBeam01] ~~~
        # pyffi.toaster:INFO:    ~~~ NiNode [WoodBeam02] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [WoodBeam02] ~~~
        # pyffi.toaster:INFO:    ~~~ NiNode [WoodBeam03] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [WoodBeam03] ~~~
        # pyffi.toaster:INFO:    ~~~ NiNode [Rusty Metal Bottom] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [Rusty Metal Bottom] ~~~
        # pyffi.toaster:INFO:    ~~~ NiNode [Rusty Metal Top] ~~~
        # pyffi.toaster:INFO:      ~~~ NiTriStrips [Rusty Metal Top] ~~~
        """

        # check optimized data
        shape = data.roots[0].collision_object.body.shape
        nose.tools.assert_equals(shape.material.material, 0)
        nose.tools.assert_true(isinstance(shape, NifFormat.bhkBoxShape))

class TestBoxCollisionOptimisation(BaseFileTestCase):

    def setUp(self):
        super(TestBoxCollisionOptimisation, self).setUp()
        self.src_name = "test_opt_collision_unpacked.nif"
        self.src_file = os.path.join(self.input_files, self.src_name)
        self.dest_file = os.path.join(self.out, self.src_name)
        shutil.copyfile(self.src_file, self.dest_file)
        assert os.path.exists(self.dest_file)

    def test_box_from_unpacked_collision_optimisation(self):
        """Test Box conversion from unpacked collision"""
        data = NifFormat.Data()
        stream = open(self.src_file, "rb")
        data.read(stream)


        # check initial data
        shape = data.roots[0].collision_object.body.shape
        nose.tools.assert_equals(shape.strips_data[0].num_vertices, 24)
        nose.tools.assert_equals(shape.material.material, 9)

        # run the spell that optimizes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=data)
        spell.recurse()

        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [TestBhkNiTriStripsShape] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        optimized box collision
        # pyffi.toaster:INFO:    ~~~ NiTriShape [Stuff] ~~~

        # check optimized data
        shape = data.roots[0].collision_object.body.shape
        nose.tools.assert_true(isinstance(shape, NifFormat.bhkConvexTransformShape))
        nose.tools.assert_equals(shape.material.material, 9)



        # Box conversion from packed collision
        # ------------------------------------
        #
        # >>> filename = nif_dir + "test_opt_collision_packed.nif"
        #
        # >>> data = NifFormat.Data()
        # >>> stream = open(filename, "rb")
        # >>> data.read(stream)
        # >>> # check initial data
        # >>> data.roots[0].collision_object.body.shape.sub_shapes[0].num_vertices
        # 24
        # >>> data.roots[0].collision_object.body.shape.data.num_vertices
        # 24
        # >>> data.roots[0].collision_object.body.shape.sub_shapes[0].material
        # 9
        # >>> # run the spell that optimizes this
        # >>> spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=data)
        # >>> spell.recurse()
        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [TestBhkPackedNiTriStripsShape] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        optimized box collision
        # pyffi.toaster:INFO:    ~~~ NiTriShape [Stuff] ~~~
        # >>> # check optimized data
        # >>> data.roots[0].collision_object.body.shape.material
        # 9
        # >>> data.roots[0].collision_object.body.shape.shape.material
        # 9
        # >>> isinstance(data.roots[0].collision_object.body.shape, NifFormat.bhkConvexTransformShape)
        # True
        # >>> isinstance(data.roots[0].collision_object.body.shape.shape, NifFormat.bhkBoxShape)
        # True
        #
        # Box conversion from mopp collision
        # ----------------------------------
        #
        # >>> filename = nif_dir + "test_opt_collision_packed.nif"
        # >>> data = NifFormat.Data()
        # >>> stream = open(filename, "rb")
        # >>> data.read(stream)
        # >>> # check initial data
        # >>> data.roots[0].collision_object.body.shape.shape.sub_shapes[0].num_vertices
        # 24
        # >>> data.roots[0].collision_object.body.shape.shape.data.num_vertices
        # 24
        # >>> data.roots[0].collision_object.body.shape.shape.sub_shapes[0].material
        # 9
        # >>> # run the spell that optimizes this
        # >>> spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=data)
        # >>> spell.recurse()
        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [TestBhkMoppBvTreeShape] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        ~~~ bhkMoppBvTreeShape [] ~~~
        # pyffi.toaster:INFO:          optimized box collision
        # pyffi.toaster:INFO:    ~~~ NiTriShape [Stuff] ~~~
        # >>> # check optimized data
        # >>> data.roots[0].collision_object.body.shape.material
        # 9
        # >>> data.roots[0].collision_object.body.shape.shape.material
        # 9
        # >>> isinstance(data.roots[0].collision_object.body.shape, NifFormat.bhkConvexTransformShape)
        # True
        # >>> isinstance(data.roots[0].collision_object.body.shape.shape, NifFormat.bhkBoxShape)
        # True
        #
        # Another regression test
        # -----------------------
        #
        # Check that a collision mesh which is not a box, but whose vertices
        # form a box, is not converted to a box.
        #
        # >>> filename = nif_dir + "test_opt_collision_to_boxshape_notabox.nif"
        # >>> data = NifFormat.Data()
        # >>> stream = open(filename, "rb")
        # >>> data.read(stream)
        # >>> # check initial data
        # >>> data.roots[0].collision_object.body.shape.__class__.__name__
        # 'bhkMoppBvTreeShape'
        # >>> # run the box spell
        # >>> spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=data)
        # >>> spell.recurse()
        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [no_box_opt_test] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        ~~~ bhkMoppBvTreeShape [] ~~~
        # >>> # check that we still have a mopp collision, and not a box collision
        # >>> data.roots[0].collision_object.body.shape.__class__.__name__
        # 'bhkMoppBvTreeShape'
