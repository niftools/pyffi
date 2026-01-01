from tests.utils import BaseNifFileTestCase
import pyffi
from pyffi.spells import Toaster
from pyffi.formats.nif import NifFormat

from tests.utils import assert_tuple_values


class TestCollisionOptimisationNif(BaseNifFileTestCase):

    def setUp(self):
        super(TestCollisionOptimisationNif, self).setUp()
        self.src_name = "test_opt_collision_to_boxshape.nif"
        super(TestCollisionOptimisationNif, self).copyFile()
        super(TestCollisionOptimisationNif, self).readNifData()

    def test_box_optimisation(self):
        # check initial data
        shape = self.data.roots[0].collision_object.body.shape
        assert shape.data.num_vertices == 8
        sub_shape = shape.sub_shapes[0]
        assert sub_shape.num_vertices == 8
        assert sub_shape.material.material == 0

        # run the spell that optimizes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=self.data)
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
        shape = self.data.roots[0].collision_object.body.shape
        assert shape.material.material == 0
        assert isinstance(shape, NifFormat.bhkBoxShape)


class TestBoxCollisionOptimisationNif(BaseNifFileTestCase):

    def setUp(self):
        super(TestBoxCollisionOptimisationNif, self).setUp()
        self.src_name = "test_opt_collision_unpacked.nif"
        super(TestBoxCollisionOptimisationNif, self).copyFile()
        super(TestBoxCollisionOptimisationNif, self).readNifData()

    def test_box_from_unpacked_collision_optimisation(self):
        """Test Box conversion from unpacked collision"""

        # check initial data
        shape = self.data.roots[0].collision_object.body.shape
        assert shape.strips_data[0].num_vertices == 24
        assert shape.material.material == 9

        # run the spell that optimizes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=self.data)
        spell.recurse()

        """
        pyffi.toaster:INFO:--- opt_collisionbox ---
        pyffi.toaster:INFO:  ~~~ NiNode [TestBhkNiTriStripsShape] ~~~
        pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        pyffi.toaster:INFO:        optimized box collision
        pyffi.toaster:INFO:    ~~~ NiTriShape [Stuff] ~~~
        """

        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape
        assert isinstance(shape, NifFormat.bhkConvexTransformShape)
        assert shape.material.material == 9


class TestPackedBoxCollisionOptimisationNif(BaseNifFileTestCase):

    def setUp(self):
        super(TestPackedBoxCollisionOptimisationNif, self).setUp()
        self.src_name = "test_opt_collision_packed.nif"
        super(TestPackedBoxCollisionOptimisationNif, self).copyFile()
        super(TestPackedBoxCollisionOptimisationNif, self).readNifData()

    def test_box_from_packed_collision_optimisation(self):
        """Test Box conversion from packed collision"""

        # check initial data
        shape = self.data.roots[0].collision_object.body.shape
        assert shape.data.num_vertices == 24
        assert shape.sub_shapes[0].num_vertices == 24
        assert shape.sub_shapes[0].material.material == 9

        # run the spell that optimizes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=self.data)
        spell.recurse()
        """
        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [TestBhkPackedNiTriStripsShape] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        optimized box collision
        # pyffi.toaster:INFO:    ~~~ NiTriShape [Stuff] ~~~
        """

        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape
        assert shape.material.material == 9
        assert isinstance(shape, NifFormat.bhkConvexTransformShape)
        assert isinstance(shape.shape, NifFormat.bhkBoxShape)

    def test_box_from_mopp_collision_optimisation(self):
        """Test Box conversion from mopp collision"""

        # check initial data
        shape = self.data.roots[0].collision_object.body.shape
        assert shape.data.num_vertices == 24
        assert shape.sub_shapes[0].num_vertices == 24
        assert shape.sub_shapes[0].material.material == 9

        # run the spell that optimizes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=self.data)
        spell.recurse()
        """
        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [TestBhkMoppBvTreeShape] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        ~~~ bhkMoppBvTreeShape [] ~~~
        # pyffi.toaster:INFO:          optimized box collision
        # pyffi.toaster:INFO:    ~~~ NiTriShape [Stuff] ~~~
        """

        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape
        assert shape.material.material == 9
        assert shape.shape.material.material == 9
        assert isinstance(shape, NifFormat.bhkConvexTransformShape)
        assert isinstance(shape.shape, NifFormat.bhkBoxShape)


class TestNotBoxCollisionOptimisationNif(BaseNifFileTestCase):

    def setUp(self):
        super(TestNotBoxCollisionOptimisationNif, self).setUp()
        self.src_name = "test_opt_collision_to_boxshape_notabox.nif"
        super(TestNotBoxCollisionOptimisationNif, self).copyFile()
        super(TestNotBoxCollisionOptimisationNif, self).readNifData()

    def test_box_from_packed_collision_optimisation(self):
        """Test that a collision mesh which is not a box, but whose vertices form a box, is not converted to a box."""

        # check initial data
        assert self.data.roots[0].collision_object.body.shape.__class__.__name__ == 'bhkMoppBvTreeShape'

        # run the box spell
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionBox(data=self.data)
        spell.recurse()
        """
        # pyffi.toaster:INFO:--- opt_collisionbox ---
        # pyffi.toaster:INFO:  ~~~ NiNode [no_box_opt_test] ~~~
        # pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        # pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        # pyffi.toaster:INFO:        ~~~ bhkMoppBvTreeShape [] ~~~
        """

        # check that we still have a mopp collision, and not a box collision
        assert self.data.roots[0].collision_object.body.shape.__class__.__name__ == 'bhkMoppBvTreeShape'


class TestMoppCollisionOptimisationNif(BaseNifFileTestCase):
    def setUp(self):
        super(TestMoppCollisionOptimisationNif, self).setUp()
        self.src_name = "test_opt_collision_complex_mopp.nif"
        super(TestMoppCollisionOptimisationNif, self).copyFile()
        super(TestMoppCollisionOptimisationNif, self).readNifData()

    def test_optimise_collision_complex_mopp(self):

        # check initial data
        shape = self.shape
        assert shape.sub_shapes[0].num_vertices == 53
        assert shape.data.num_vertices == 53
        assert shape.data.num_triangles == 102

        hktriangle = self.data.roots[0].collision_object.body.shape.shape.data.triangles[-1]
        triangle = hktriangle.triangle
        assert hktriangle.welding_info == 18924

        assert_tuple_values((triangle.v_1, triangle.v_2, triangle.v_3), (13, 17, 5))
        normal = hktriangle.normal
        assert_tuple_values((-0.9038461, 0.19667668, - 0.37997436), (normal.x, normal.y, normal.z))

        # run the spell that fixes this
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionGeometry(data=self.data)
        spell.recurse()

        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape.shape
        assert shape.sub_shapes[0].num_vertices == 51
        assert shape.data.num_vertices == 51
        assert shape.data.num_triangles == 98

        hktriangle = self.data.roots[0].collision_object.body.shape.shape.data.triangles[-1]

        triangle = hktriangle.triangle
        assert_tuple_values((triangle.v_1, triangle.v_2, triangle.v_3), (12, 16, 4))
        assert hktriangle.welding_info == 18924
        assert_tuple_values((-0.9038461, 0.19667668, - 0.37997436), (normal.x, normal.y, normal.z))

        """
            pyffi.toaster: INFO:--- opt_collisiongeometry ---
            pyffi.toaster: INFO:  ~~~ NiNode[Scene Root] ~~~
            pyffi.toaster: INFO:    ~~~ bhkCollisionObject[] ~~~
            pyffi.toaster: INFO:      ~~~ bhkRigidBody[] ~~~
            pyffi.toaster: INFO:        ~~~ bhkMoppBvTreeShape[]~~~
            pyffi.toaster: INFO:          optimizing mopp
            pyffi.toaster: INFO:          removing duplicate vertices
            pyffi.toaster: INFO:          (processing subshape 0)
            pyffi.toaster: INFO:          (num vertices in collision shape was 53 and is now 51)
            pyffi.toaster: INFO:          removing duplicate triangles
            pyffi.toaster: INFO:          (num triangles in collision shape was 102 and is now 98)
            pyffi.toaster: INFO:    ~~~ NiTriShape[]
            ~~~
        """


class TestUnpackedCollisionOptimisationNif(BaseNifFileTestCase):

    def setUp(self):
        super(TestUnpackedCollisionOptimisationNif, self).setUp()
        self.src_name = "test_opt_collision_unpacked.nif"
        super(TestUnpackedCollisionOptimisationNif, self).copyFile()
        super(TestUnpackedCollisionOptimisationNif, self).readNifData()

    def test_optimise_collision_unpacked(self):
        """Test unpacked collision """

        # check initial data
        strip = self.data.roots[0].collision_object.body.shape.strips_data[0]
        assert strip.num_vertices == 24
        assert strip.num_triangles == 32

        # run the spell
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionGeometry(data=self.data)
        spell.recurse()

        """
        pyffi.toaster: INFO:--- opt_collisiongeometry - --
        pyffi.toaster: INFO:  ~~~ NiNode[TestBhkNiTriStripsShape] ~~~
        pyffi.toaster: INFO:    ~~~ bhkCollisionObject[] ~~~
        pyffi.toaster: INFO:      ~~~ bhkRigidBodyT[] ~~~
        pyffi.toaster: INFO:        packing collision
        pyffi.toaster: INFO:        adding mopp
        """
        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape.shape
        assert shape.sub_shapes[0].num_vertices == 8
        assert shape.data.num_vertices == 8
        assert shape.data.num_triangles == 12


class TestPackedCollisionOptimisationNif(BaseNifFileTestCase):

    def setUp(self):
        super(TestPackedCollisionOptimisationNif, self).setUp()
        self.src_name = "test_opt_collision_packed.nif"
        super(TestPackedCollisionOptimisationNif, self).copyFile()
        super(TestPackedCollisionOptimisationNif, self).readNifData()

    def test_optimise_collision_packed(self):
        """Test packed collision """

        # check initial data
        shape = self.data.roots[0].collision_object.body.shape
        assert shape.sub_shapes[0].num_vertices == 24
        assert shape.data.num_vertices == 24
        assert shape.data.num_triangles == 12

        # run the spell
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionGeometry(data=self.data)
        spell.recurse()
        """
        pyffi.toaster:INFO:--- opt_collisiongeometry ---
        pyffi.toaster:INFO:  ~~~ NiNode [TestBhkPackedNiTriStripsShape] ~~~
        pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        pyffi.toaster:INFO:        adding mopp
        pyffi.toaster:INFO:        optimizing mopp
        pyffi.toaster:INFO:        removing duplicate vertices
        pyffi.toaster:INFO:        (processing subshape 0)
        pyffi.toaster:INFO:        (num vertices in collision shape was 24 and is now 8)
        pyffi.toaster:INFO:        removing duplicate triangles
        pyffi.toaster:INFO:        (num triangles in collision shape was 12 and is now 12)
        pyffi.toaster:INFO:    ~~~ NiTriShape [Stuff] ~~~
        """

        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape.shape
        assert shape.sub_shapes[0].num_vertices == 8
        assert shape.data.num_vertices == 8
        assert shape.data.num_triangles == 12


class TestMoppCollisionOptimisationNif(BaseNifFileTestCase):

    def setUp(self):
        super(TestMoppCollisionOptimisationNif, self).setUp()
        self.src_name = "test_opt_collision_mopp.nif"
        super(TestMoppCollisionOptimisationNif, self).copyFile()
        super(TestMoppCollisionOptimisationNif, self).readNifData()

    def test_optimise_collision_packed(self):
        """Test packed collision """

        # check initial data
        shape = self.data.roots[0].collision_object.body.shape.shape
        assert shape.sub_shapes[0].num_vertices == 24
        assert shape.data.num_vertices == 24
        assert shape.data.num_triangles == 12

        # run the spell
        spell = pyffi.spells.nif.optimize.SpellOptimizeCollisionGeometry(data=self.data)
        spell.recurse()

        """
        pyffi.toaster:INFO:--- opt_collisiongeometry ---
        pyffi.toaster:INFO:  ~~~ NiNode [TestBhkMoppBvTreeShape] ~~~
        pyffi.toaster:INFO:    ~~~ bhkCollisionObject [] ~~~
        pyffi.toaster:INFO:      ~~~ bhkRigidBodyT [] ~~~
        pyffi.toaster:INFO:        ~~~ bhkMoppBvTreeShape [] ~~~
        pyffi.toaster:INFO:          optimizing mopp
        pyffi.toaster:INFO:          removing duplicate vertices
        pyffi.toaster:INFO:          (processing subshape 0)
        pyffi.toaster:INFO:          (num vertices in collision shape was 24 and is now 8)
        pyffi.toaster:INFO:          removing duplicate triangles
        pyffi.toaster:INFO:          (num triangles in collision shape was 12 and is now 12)
        pyffi.toaster:INFO:    ~~~ NiTriShape [Stuff] ~~~
        """
        # check optimized data
        shape = self.data.roots[0].collision_object.body.shape.shape
        assert shape.sub_shapes[0].num_vertices == 8
        assert shape.data.num_vertices == 8
        assert shape.data.num_triangles == 12
