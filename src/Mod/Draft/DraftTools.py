# -*- coding: utf8 -*-
# ***************************************************************************
# *   Copyright (c) 2009, 2010 Yorik van Havre <yorik@uncreated.net>        *
# *   Copyright (c) 2009, 2010 Ken Cline <cline@frii.com>                   *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""Provide GUI commands of the Draft Workbench.

This module loads all graphical commands of the Draft Workbench,
that is, those actions that can be called from menus and buttons.
This module must be imported only when the graphical user interface
is available, for example, during the workbench definition in `IntiGui.py`.
"""
## @package DraftTools
#  \ingroup DRAFT
#  \brief Provide GUI commands of the Draft workbench.
#
#  This module contains all the graphical commands of the Draft workbench,
#  that is, those actions that can be called from menus and buttons.

# ---------------------------------------------------------------------------
# Generic stuff
# ---------------------------------------------------------------------------
import math
import sys
from PySide import QtCore, QtGui
from pivy import coin

import FreeCAD
import FreeCADGui
from FreeCAD import Vector

import Draft
import Draft_rc
import DraftGui  # Initializes the DraftToolBar class
import DraftVecUtils
import WorkingPlane
from draftutils.todo import ToDo
from draftutils.translate import translate
import draftguitools.gui_snapper as gui_snapper
import draftguitools.gui_trackers as trackers

# The module is used to prevent complaints from code checkers (flake8)
True if Draft_rc.__name__ else False
True if DraftGui.__name__ else False

__title__ = "FreeCAD Draft Workbench GUI Tools"
__author__ = ("Yorik van Havre, Werner Mayer, Martin Burbaum, Ken Cline, "
              "Dmitry Chigrin")
__url__ = "https://www.freecadweb.org"

if not hasattr(FreeCADGui, "Snapper"):
    FreeCADGui.Snapper = gui_snapper.Snapper()

if not hasattr(FreeCAD, "DraftWorkingPlane"):
    FreeCAD.DraftWorkingPlane = WorkingPlane.plane()

# ---------------------------------------------------------------------------
# Commands that have been migrated to their own modules
# ---------------------------------------------------------------------------
import draftguitools.gui_edit
import draftguitools.gui_selectplane
import draftguitools.gui_planeproxy
from draftguitools.gui_lineops import FinishLine
from draftguitools.gui_lineops import CloseLine
from draftguitools.gui_lineops import UndoLine
from draftguitools.gui_togglemodes import ToggleConstructionMode
from draftguitools.gui_togglemodes import ToggleContinueMode
from draftguitools.gui_togglemodes import ToggleDisplayMode
from draftguitools.gui_groups import AddToGroup
from draftguitools.gui_groups import SelectGroup
from draftguitools.gui_groups import SetAutoGroup
from draftguitools.gui_groups import Draft_AddConstruction
from draftguitools.gui_grid import ToggleGrid
from draftguitools.gui_heal import Heal
from draftguitools.gui_dimension_ops import Draft_FlipDimension
from draftguitools.gui_lineslope import Draft_Slope
import draftguitools.gui_arrays
import draftguitools.gui_annotationstyleeditor
# import DraftFillet
import drafttaskpanels.task_scale as task_scale

# ---------------------------------------------------------------------------
# Preflight stuff
# ---------------------------------------------------------------------------
# update the translation engine
FreeCADGui.updateLocale()

# sets the default working plane
plane = WorkingPlane.plane()
FreeCAD.DraftWorkingPlane = plane
defaultWP = Draft.getParam("defaultWP",1)
if defaultWP == 1: plane.alignToPointAndAxis(Vector(0,0,0), Vector(0,0,1), 0)
elif defaultWP == 2: plane.alignToPointAndAxis(Vector(0,0,0), Vector(0,1,0), 0)
elif defaultWP == 3: plane.alignToPointAndAxis(Vector(0,0,0), Vector(1,0,0), 0)

# last snapped objects, for quick intersection calculation
lastObj = [0,0]

# Set modifier keys
from draftguitools.gui_tool_utils import MODCONSTRAIN
from draftguitools.gui_tool_utils import MODSNAP
from draftguitools.gui_tool_utils import MODALT

# ---------------------------------------------------------------------------
# General functions
# ---------------------------------------------------------------------------
from draftguitools.gui_tool_utils import formatUnit

from draftguitools.gui_tool_utils import selectObject

from draftguitools.gui_tool_utils import getPoint

from draftguitools.gui_tool_utils import getSupport

from draftguitools.gui_tool_utils import setWorkingPlaneToObjectUnderCursor

from draftguitools.gui_tool_utils import setWorkingPlaneToSelectedObject

from draftguitools.gui_tool_utils import hasMod

from draftguitools.gui_tool_utils import setMod

# ---------------------------------------------------------------------------
# Base Class
# ---------------------------------------------------------------------------
from draftguitools.gui_base_original import DraftTool

# ---------------------------------------------------------------------------
# Geometry constructors
# ---------------------------------------------------------------------------
from draftguitools.gui_tool_utils import redraw3DView

from draftguitools.gui_base_original import Creator

from draftguitools.gui_lines import Line
from draftguitools.gui_lines import Wire
from draftguitools.gui_splines import BSpline
from draftguitools.gui_beziers import BezCurve
from draftguitools.gui_beziers import CubicBezCurve
from draftguitools.gui_beziers import BezierGroup
from draftguitools.gui_rectangles import Rectangle
from draftguitools.gui_arcs import Arc
from draftguitools.gui_arcs import Draft_Arc_3Points
from draftguitools.gui_circles import Circle
from draftguitools.gui_polygons import Polygon
from draftguitools.gui_ellipses import Ellipse
from draftguitools.gui_texts import Text
from draftguitools.gui_dimensions import Dimension
from draftguitools.gui_shapestrings import ShapeString
from draftguitools.gui_points import Point
from draftguitools.gui_facebinders import Draft_Facebinder
from draftguitools.gui_labels import Draft_Label

# ---------------------------------------------------------------------------
# Modifier functions
# ---------------------------------------------------------------------------
from draftguitools.gui_base_original import Modifier


class Move(Modifier):
    """The Draft_Move FreeCAD command definition"""

    def __init__(self):
        Modifier.__init__(self)

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Move',
                'Accel' : "M, V",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Move", "Move"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Move", "Moves the selected objects between 2 points. CTRL to snap, SHIFT to constrain")}

    def Activated(self):
        self.name = translate("draft","Move", utf8_decode=True)
        Modifier.Activated(self, self.name,
                           is_subtool=isinstance(FreeCAD.activeDraftCommand, SubelementHighlight))
        if not self.ui:
            return
        self.ghosts = []
        self.get_object_selection()

    def get_object_selection(self):
        if FreeCADGui.Selection.getSelectionEx():
            return self.proceed()
        self.ui.selectUi()
        FreeCAD.Console.PrintMessage(translate("draft", "Select an object to move")+"\n")
        self.call = self.view.addEventCallback("SoEvent", selectObject)

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        self.selected_objects = FreeCADGui.Selection.getSelection()
        self.selected_objects = Draft.getGroupContents(self.selected_objects, addgroups=True, spaces=True, noarchchild=True)
        self.selected_subelements = FreeCADGui.Selection.getSelectionEx()
        self.ui.lineUi(self.name)
        self.ui.modUi()
        if self.copymode:
            self.ui.isCopy.setChecked(True)
        self.ui.xValue.setFocus()
        self.ui.xValue.selectAll()
        self.call = self.view.addEventCallback("SoEvent", self.action)
        FreeCAD.Console.PrintMessage(translate("draft", "Pick start point")+"\n")

    def finish(self,closed=False,cont=False):
        for ghost in self.ghosts:
            ghost.finalize()
        if cont and self.ui:
            if self.ui.continueMode:
                ToDo.delayAfter(self.Activated, [])
        Modifier.finish(self)

    def action(self,arg):
        """scene event handler"""
        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "ESCAPE":
            self.finish()
        elif arg["Type"] == "SoLocation2Event":
            self.handle_mouse_move_event(arg)
        elif arg["Type"] == "SoMouseButtonEvent" \
            and arg["State"] == "DOWN" \
            and arg["Button"] == "BUTTON1":
            self.handle_mouse_click_event(arg)

    def handle_mouse_move_event(self, arg):
        for ghost in self.ghosts:
            ghost.off()
        self.point, ctrlPoint, info = getPoint(self,arg)
        if (len(self.node) > 0):
            last = self.node[len(self.node)-1]
            self.vector = self.point.sub(last)
            for ghost in self.ghosts:
                ghost.move(self.vector)
                ghost.on()
        if self.extendedCopy:
            if not hasMod(arg,MODALT): self.finish()
        redraw3DView()

    def handle_mouse_click_event(self, arg):
        if not self.ghosts:
            self.set_ghosts()
        if not self.point:
            return
        self.ui.redraw()
        if self.node == []:
            self.node.append(self.point)
            self.ui.isRelative.show()
            for ghost in self.ghosts:
                ghost.on()
            FreeCAD.Console.PrintMessage(translate("draft", "Pick end point")+"\n")
            if self.planetrack:
                self.planetrack.set(self.point)
        else:
            last = self.node[0]
            self.vector = self.point.sub(last)
            self.move()
            if hasMod(arg,MODALT):
                self.extendedCopy = True
            else:
                self.finish(cont=True)

    def set_ghosts(self):
        if self.ui.isSubelementMode.isChecked():
            return self.set_subelement_ghosts()
        self.ghosts = [trackers.ghostTracker(self.selected_objects)]

    def set_subelement_ghosts(self):
        import Part
        for object in self.selected_subelements:
            for subelement in object.SubObjects:
                if isinstance(subelement, Part.Vertex) \
                    or isinstance(subelement, Part.Edge):
                    self.ghosts.append(trackers.ghostTracker(subelement))

    def move(self):
        if self.ui.isSubelementMode.isChecked():
            self.move_subelements()
        else:
            self.move_object()

    def move_subelements(self):
        try:
            if self.ui.isCopy.isChecked():
                self.commit(translate("draft", "Copy"), self.build_copy_subelements_command())
            else:
                self.commit(translate("draft", "Move"), self.build_move_subelements_command())
        except:
            FreeCAD.Console.PrintError(translate("draft", "Some subelements could not be moved."))

    def build_copy_subelements_command(self):
        import Part
        command = []
        arguments = []
        for object in self.selected_subelements:
            for index, subelement in enumerate(object.SubObjects):
                if not isinstance(subelement, Part.Edge):
                    continue
                arguments.append('[FreeCAD.ActiveDocument.{}, {}, {}]'.format(
                    object.ObjectName,
                    int(object.SubElementNames[index][len("Edge"):])-1,
                    DraftVecUtils.toString(self.vector)))
        command.append('Draft.copyMovedEdges([{}])'.format(','.join(arguments)))
        command.append('FreeCAD.ActiveDocument.recompute()')
        return command

    def build_move_subelements_command(self):
        import Part
        command = []
        for object in self.selected_subelements:
            for index, subelement in enumerate(object.SubObjects):
                if isinstance(subelement, Part.Vertex):
                    command.append('Draft.moveVertex(FreeCAD.ActiveDocument.{}, {}, {})'.format(
                        object.ObjectName,
                        int(object.SubElementNames[index][len("Vertex"):])-1,
                        DraftVecUtils.toString(self.vector)
                        ))
                elif isinstance(subelement, Part.Edge):
                    command.append('Draft.moveEdge(FreeCAD.ActiveDocument.{}, {}, {})'.format(
                        object.ObjectName,
                        int(object.SubElementNames[index][len("Edge"):])-1,
                        DraftVecUtils.toString(self.vector)
                        ))
        command.append('FreeCAD.ActiveDocument.recompute()')
        return command

    def move_object(self):
        objects = '[' + ','.join(['FreeCAD.ActiveDocument.' + object.Name for object in self.selected_objects]) + ']'
        FreeCADGui.addModule("Draft")
        self.commit(translate("draft","Copy" if self.ui.isCopy.isChecked() else "Move"),
            ['Draft.move('+objects+','+DraftVecUtils.toString(self.vector)+',copy='+str(self.ui.isCopy.isChecked())+')', 'FreeCAD.ActiveDocument.recompute()'])

    def numericInput(self,numx,numy,numz):
        """this function gets called by the toolbar when valid x, y, and z have been entered there"""
        self.point = Vector(numx,numy,numz)
        if not self.node:
            self.node.append(self.point)
            self.ui.isRelative.show()
            self.ui.isCopy.show()
            for ghost in self.ghosts:
                ghost.on()
            FreeCAD.Console.PrintMessage(translate("draft", "Pick end point")+"\n")
        else:
            last = self.node[-1]
            self.vector = self.point.sub(last)
            self.move()
            self.finish()


class ApplyStyle(Modifier):
    """The Draft_ApplyStyle FreeCA command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Apply',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_ApplyStyle", "Apply Current Style"),
                'ToolTip' : QtCore.QT_TRANSLATE_NOOP("Draft_ApplyStyle", "Applies current line width and color to selected objects")}

    def IsActive(self):
        if FreeCADGui.Selection.getSelection():
            return True
        else:
            return False

    def Activated(self):
        Modifier.Activated(self)
        if self.ui:
            self.sel = FreeCADGui.Selection.getSelection()
            if (len(self.sel)>0):
                FreeCADGui.addModule("Draft")
                c = []
                for ob in self.sel:
                    if (ob.Type == "App::DocumentObjectGroup"):
                        c.extend(self.formatGroup(ob))
                    else:
                        c.append('Draft.formatObject(FreeCAD.ActiveDocument.'+ob.Name+')')
                self.commit(translate("draft","Change Style"),c)

    def formatGroup(self,grpob):
        FreeCADGui.addModule("Draft")
        c=[]
        for ob in grpob.Group:
            if (ob.Type == "App::DocumentObjectGroup"):
                c.extend(self.formatGroup(ob))
            else:
                c.append('Draft.formatObject(FreeCAD.ActiveDocument.'+ob.Name+')')

class Rotate(Modifier):
    """The Draft_Rotate FreeCAD command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Rotate',
                'Accel' : "R, O",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Rotate", "Rotate"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Rotate", "Rotates the selected objects. CTRL to snap, SHIFT to constrain, ALT creates a copy")}

    def Activated(self):
        Modifier.Activated(self,"Rotate")
        if not self.ui:
            return
        self.ghosts = []
        self.arctrack = None
        self.get_object_selection()

    def get_object_selection(self):
        if FreeCADGui.Selection.getSelection():
            return self.proceed()
        self.ui.selectUi()
        FreeCAD.Console.PrintMessage(translate("draft", "Select an object to rotate")+"\n")
        self.call = self.view.addEventCallback("SoEvent", selectObject)

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent", self.call)
        self.selected_objects = FreeCADGui.Selection.getSelection()
        self.selected_objects = Draft.getGroupContents(self.selected_objects, addgroups=True, spaces=True, noarchchild=True)
        self.selected_subelements = FreeCADGui.Selection.getSelectionEx()
        self.step = 0
        self.center = None
        self.ui.rotateSetCenterUi()
        self.ui.modUi()
        self.ui.setTitle(translate("draft","Rotate"))
        self.arctrack = trackers.arcTracker()
        self.call = self.view.addEventCallback("SoEvent",self.action)
        FreeCAD.Console.PrintMessage(translate("draft", "Pick rotation center")+"\n")

    def action(self, arg):
        """scene event handler"""
        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "ESCAPE":
                self.finish()
        elif arg["Type"] == "SoLocation2Event":
            self.handle_mouse_move_event(arg)
        elif arg["Type"] == "SoMouseButtonEvent" \
            and arg["State"] == "DOWN" \
            and arg["Button"] == "BUTTON1":
            self.handle_mouse_click_event(arg)

    def handle_mouse_move_event(self, arg):
        for ghost in self.ghosts:
            ghost.off()
        self.point,ctrlPoint,info = getPoint(self,arg)
        # this is to make sure radius is what you see on screen
        if self.center and DraftVecUtils.dist(self.point,self.center):
            viewdelta = DraftVecUtils.project(self.point.sub(self.center), plane.axis)
            if not DraftVecUtils.isNull(viewdelta):
                self.point = self.point.add(viewdelta.negative())
        if self.extendedCopy:
            if not hasMod(arg,MODALT):
                self.step = 3
                self.finish()
        if (self.step == 0):
            pass
        elif (self.step == 1):
            currentrad = DraftVecUtils.dist(self.point,self.center)
            if (currentrad != 0):
                angle = DraftVecUtils.angle(plane.u, self.point.sub(self.center), plane.axis)
            else: angle = 0
            self.ui.setRadiusValue(math.degrees(angle),unit="Angle")
            self.firstangle = angle
            self.ui.radiusValue.setFocus()
            self.ui.radiusValue.selectAll()
        elif (self.step == 2):
            currentrad = DraftVecUtils.dist(self.point,self.center)
            if (currentrad != 0):
                angle = DraftVecUtils.angle(plane.u, self.point.sub(self.center), plane.axis)
            else: angle = 0
            if (angle < self.firstangle):
                sweep = (2*math.pi-self.firstangle)+angle
            else:
                sweep = angle - self.firstangle
            self.arctrack.setApertureAngle(sweep)
            for ghost in self.ghosts:
                ghost.rotate(plane.axis,sweep)
                ghost.on()
            self.ui.setRadiusValue(math.degrees(sweep), 'Angle')
            self.ui.radiusValue.setFocus()
            self.ui.radiusValue.selectAll()
        redraw3DView()

    def handle_mouse_click_event(self, arg):
        if not self.point:
            return
        if self.step == 0:
            self.set_center()
        elif self.step == 1:
            self.set_start_point()
        else:
            self.set_rotation_angle(arg)

    def set_center(self):
        if not self.ghosts:
            self.set_ghosts()
        self.center = self.point
        self.node = [self.point]
        self.ui.radiusUi()
        self.ui.radiusValue.setText(FreeCAD.Units.Quantity(0,FreeCAD.Units.Angle).UserString)
        self.ui.hasFill.hide()
        self.ui.labelRadius.setText(translate("draft","Base angle"))
        self.ui.radiusValue.setToolTip(translate("draft","The base angle you wish to start the rotation from"))
        self.arctrack.setCenter(self.center)
        for ghost in self.ghosts:
            ghost.center(self.center)
        self.step = 1
        FreeCAD.Console.PrintMessage(translate("draft", "Pick base angle")+"\n")
        if self.planetrack:
            self.planetrack.set(self.point)

    def set_start_point(self):
        self.ui.labelRadius.setText(translate("draft","Rotation"))
        self.ui.radiusValue.setToolTip(translate("draft", "The amount of rotation you wish to perform. The final angle will be the base angle plus this amount."))
        self.rad = DraftVecUtils.dist(self.point,self.center)
        self.arctrack.on()
        self.arctrack.setStartPoint(self.point)
        for ghost in self.ghosts:
            ghost.on()
        self.step = 2
        FreeCAD.Console.PrintMessage(translate("draft", "Pick rotation angle")+"\n")

    def set_rotation_angle(self, arg):
        currentrad = DraftVecUtils.dist(self.point,self.center)
        angle = self.point.sub(self.center).getAngle(plane.u)
        if DraftVecUtils.project(self.point.sub(self.center), plane.v).getAngle(plane.v) > 1:
            angle = -angle
        if (angle < self.firstangle):
            self.angle = (2*math.pi-self.firstangle)+angle
        else:
            self.angle = angle - self.firstangle
        self.rotate(self.ui.isCopy.isChecked() or hasMod(arg,MODALT))
        if hasMod(arg,MODALT):
            self.extendedCopy = True
        else:
            self.finish(cont=True)

    def set_ghosts(self):
        if self.ui.isSubelementMode.isChecked():
            return self.set_subelement_ghosts()
        self.ghosts = [trackers.ghostTracker(self.selected_objects)]

    def set_subelement_ghosts(self):
        import Part
        for object in self.selected_subelements:
            for subelement in object.SubObjects:
                if isinstance(subelement, Part.Vertex) \
                    or isinstance(subelement, Part.Edge):
                    self.ghosts.append(trackers.ghostTracker(subelement))

    def finish(self, closed=False, cont=False):
        """finishes the arc"""
        if self.arctrack:
            self.arctrack.finalize()
        for ghost in self.ghosts:
            ghost.finalize()
        if cont and self.ui:
            if self.ui.continueMode:
                ToDo.delayAfter(self.Activated, [])
        Modifier.finish(self)
        if self.doc:
            self.doc.recompute()

    def rotate(self, is_copy=False):
        if self.ui.isSubelementMode.isChecked():
            self.rotate_subelements(is_copy)
        else:
            self.rotate_object(is_copy)

    def rotate_subelements(self, is_copy):
        try:
            if is_copy:
                self.commit(translate("draft", "Copy"), self.build_copy_subelements_command())
            else:
                self.commit(translate("draft", "Rotate"), self.build_rotate_subelements_command())
        except:
            FreeCAD.Console.PrintError(translate("draft", "Some subelements could not be moved."))

    def build_copy_subelements_command(self):
        import Part
        command = []
        arguments = []
        for object in self.selected_subelements:
            for index, subelement in enumerate(object.SubObjects):
                if not isinstance(subelement, Part.Edge):
                    continue
                arguments.append('[FreeCAD.ActiveDocument.{}, {}, {}, {}, {}]'.format(
                    object.ObjectName,
                    int(object.SubElementNames[index][len("Edge"):])-1,
                    math.degrees(self.angle),
                    DraftVecUtils.toString(self.center),
                    DraftVecUtils.toString(plane.axis)))
        command.append('Draft.copyRotatedEdges([{}])'.format(','.join(arguments)))
        command.append('FreeCAD.ActiveDocument.recompute()')
        return command

    def build_rotate_subelements_command(self):
        import Part
        command = []
        for object in self.selected_subelements:
            for index, subelement in enumerate(object.SubObjects):
                if isinstance(subelement, Part.Vertex):
                    command.append('Draft.rotateVertex(FreeCAD.ActiveDocument.{}, {}, {}, {}, {})'.format(
                        object.ObjectName,
                        int(object.SubElementNames[index][len("Vertex"):])-1,
                        math.degrees(self.angle),
                        DraftVecUtils.toString(self.center),
                        DraftVecUtils.toString(plane.axis)))
                elif isinstance(subelement, Part.Edge):
                    command.append('Draft.rotateEdge(FreeCAD.ActiveDocument.{}, {}, {}, {}, {})'.format(
                        object.ObjectName,
                        int(object.SubElementNames[index][len("Edge"):])-1,
                        math.degrees(self.angle),
                        DraftVecUtils.toString(self.center),
                        DraftVecUtils.toString(plane.axis)))
        command.append('FreeCAD.ActiveDocument.recompute()')
        return command

    def rotate_object(self, is_copy):
        objects = '[' + ','.join(['FreeCAD.ActiveDocument.' + object.Name for object in self.selected_objects]) + ']'
        FreeCADGui.addModule("Draft")
        self.commit(translate("draft","Copy" if is_copy else "Rotate"),
            ['Draft.rotate({},{},{},axis={},copy={})'.format(
                objects,
                math.degrees(self.angle),
                DraftVecUtils.toString(self.center),
                DraftVecUtils.toString(plane.axis),
                is_copy
            ),
            'FreeCAD.ActiveDocument.recompute()'])

    def numericInput(self,numx,numy,numz):
        """this function gets called by the toolbar when valid x, y, and z have been entered there"""
        self.center = Vector(numx,numy,numz)
        self.node = [self.center]
        self.arctrack.setCenter(self.center)
        for ghost in self.ghosts:
            ghost.center(self.center)
        self.ui.radiusUi()
        self.ui.hasFill.hide()
        self.ui.labelRadius.setText(translate("draft","Base angle"))
        self.ui.radiusValue.setToolTip(translate("draft","The base angle you wish to start the rotation from"))
        self.ui.radiusValue.setText(FreeCAD.Units.Quantity(0,FreeCAD.Units.Angle).UserString)
        self.step = 1
        FreeCAD.Console.PrintMessage(translate("draft", "Pick base angle")+"\n")

    def numericRadius(self,rad):
        """this function gets called by the toolbar when valid radius have been entered there"""
        if (self.step == 1):
            self.ui.labelRadius.setText(translate("draft","Rotation"))
            self.ui.radiusValue.setToolTip(translate("draft","The amount of rotation you wish to perform. The final angle will be the base angle plus this amount."))
            self.ui.radiusValue.setText(FreeCAD.Units.Quantity(0,FreeCAD.Units.Angle).UserString)
            self.firstangle = math.radians(rad)
            self.arctrack.setStartAngle(self.firstangle)
            self.arctrack.on()
            for ghost in self.ghosts:
                ghost.on()
            self.step = 2
            FreeCAD.Console.PrintMessage(translate("draft", "Pick rotation angle")+"\n")
        else:
            self.angle = math.radians(rad)
            self.rotate(self.ui.isCopy.isChecked())
            self.finish(cont=True)


class Offset(Modifier):
    """The Draft_Offset FreeCAD command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Offset',
                'Accel' : "O, S",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Offset", "Offset"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Offset", "Offsets the active object. CTRL to snap, SHIFT to constrain, ALT to copy")}

    def Activated(self):
        self.running = False
        Modifier.Activated(self,"Offset")
        self.ghost = None
        self.linetrack = None
        self.arctrack = None
        if self.ui:
            if not FreeCADGui.Selection.getSelection():
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Select an object to offset")+"\n")
                self.call = self.view.addEventCallback("SoEvent",selectObject)
            elif len(FreeCADGui.Selection.getSelection()) > 1:
                FreeCAD.Console.PrintWarning(translate("draft", "Offset only works on one object at a time")+"\n")
            else:
                self.proceed()

    def proceed(self):
        if self.call: self.view.removeEventCallback("SoEvent",self.call)
        self.sel = FreeCADGui.Selection.getSelection()[0]
        if not self.sel.isDerivedFrom("Part::Feature"):
            FreeCAD.Console.PrintWarning(translate("draft", "Cannot offset this object type")+"\n")
            self.finish()
        else:
            self.step = 0
            self.dvec = None
            self.npts = None
            self.constrainSeg = None
            self.ui.offsetUi()
            self.linetrack = trackers.lineTracker()
            self.faces = False
            self.shape = self.sel.Shape
            self.mode = None
            if Draft.getType(self.sel) in ["Circle","Arc"]:
                self.ghost = trackers.arcTracker()
                self.mode = "Circle"
                self.center = self.shape.Edges[0].Curve.Center
                self.ghost.setCenter(self.center)
                self.ghost.setStartAngle(math.radians(self.sel.FirstAngle))
                self.ghost.setEndAngle(math.radians(self.sel.LastAngle))
            elif Draft.getType(self.sel) == "BSpline":
                self.ghost = trackers.bsplineTracker(points=self.sel.Points)
                self.mode = "BSpline"
            elif Draft.getType(self.sel) == "BezCurve":
                FreeCAD.Console.PrintWarning(translate("draft", "Sorry, offset of Bezier curves is currently still not supported")+"\n")
                self.finish()
                return
            else:
                if len(self.sel.Shape.Edges) == 1:
                    import Part
                    if isinstance(self.sel.Shape.Edges[0].Curve,Part.Circle):
                        self.ghost = trackers.arcTracker()
                        self.mode = "Circle"
                        self.center = self.shape.Edges[0].Curve.Center
                        self.ghost.setCenter(self.center)
                        if len(self.sel.Shape.Vertexes) > 1:
                            self.ghost.setStartAngle(self.sel.Shape.Edges[0].FirstParameter)
                            self.ghost.setEndAngle(self.sel.Shape.Edges[0].LastParameter)
                if not self.ghost:
                    self.ghost = trackers.wireTracker(self.shape)
                    self.mode = "Wire"
            self.call = self.view.addEventCallback("SoEvent",self.action)
            FreeCAD.Console.PrintMessage(translate("draft", "Pick distance")+"\n")
            if self.planetrack:
                self.planetrack.set(self.shape.Vertexes[0].Point)
            self.running = True

    def action(self,arg):
        """scene event handler"""
        import DraftGeomUtils
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
        elif arg["Type"] == "SoLocation2Event":
            self.point,ctrlPoint,info = getPoint(self,arg)
            if hasMod(arg,MODCONSTRAIN) and self.constrainSeg:
                dist = DraftGeomUtils.findPerpendicular(self.point,self.shape,self.constrainSeg[1])
            else:
                dist = DraftGeomUtils.findPerpendicular(self.point,self.shape.Edges)
            if dist:
                self.ghost.on()
                if self.mode == "Wire":
                    d = dist[0].negative()
                    v1 = DraftGeomUtils.getTangent(self.shape.Edges[0],self.point)
                    v2 = DraftGeomUtils.getTangent(self.shape.Edges[dist[1]],self.point)
                    a = -DraftVecUtils.angle(v1,v2)
                    self.dvec = DraftVecUtils.rotate(d,a,plane.axis)
                    occmode = self.ui.occOffset.isChecked()
                    self.ghost.update(DraftGeomUtils.offsetWire(self.shape,self.dvec,occ=occmode),forceclosed=occmode)
                elif self.mode == "BSpline":
                    d = dist[0].negative()
                    e = self.shape.Edges[0]
                    basetan = DraftGeomUtils.getTangent(e,self.point)
                    self.npts = []
                    for p in self.sel.Points:
                        currtan = DraftGeomUtils.getTangent(e,p)
                        a = -DraftVecUtils.angle(currtan,basetan)
                        self.dvec = DraftVecUtils.rotate(d,a,plane.axis)
                        self.npts.append(p.add(self.dvec))
                    self.ghost.update(self.npts)
                elif self.mode == "Circle":
                    self.dvec = self.point.sub(self.center).Length
                    self.ghost.setRadius(self.dvec)
                self.constrainSeg = dist
                self.linetrack.on()
                self.linetrack.p1(self.point)
                self.linetrack.p2(self.point.add(dist[0]))
                self.ui.setRadiusValue(dist[0].Length,unit="Length")
            else:
                self.dvec = None
                self.ghost.off()
                self.constrainSeg = None
                self.linetrack.off()
                self.ui.radiusValue.setText("off")
            self.ui.radiusValue.setFocus()
            self.ui.radiusValue.selectAll()
            if self.extendedCopy:
                if not hasMod(arg,MODALT): self.finish()
            redraw3DView()

        elif arg["Type"] == "SoMouseButtonEvent":
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):
                copymode = False
                occmode = self.ui.occOffset.isChecked()
                if hasMod(arg,MODALT) or self.ui.isCopy.isChecked(): copymode = True
                FreeCADGui.addModule("Draft")
                if self.npts:
                    print("offset:npts=",self.npts)
                    self.commit(translate("draft","Offset"),
                                ['Draft.offset(FreeCAD.ActiveDocument.'+self.sel.Name+','+DraftVecUtils.toString(self.npts)+',copy='+str(copymode)+')',
                                 'FreeCAD.ActiveDocument.recompute()'])
                elif self.dvec:
                    if isinstance(self.dvec,float):
                        d = str(self.dvec)
                    else:
                        d = DraftVecUtils.toString(self.dvec)
                    self.commit(translate("draft","Offset"),
                                ['Draft.offset(FreeCAD.ActiveDocument.'+self.sel.Name+','+d+',copy='+str(copymode)+',occ='+str(occmode)+')',
                                 'FreeCAD.ActiveDocument.recompute()'])
                if hasMod(arg,MODALT):
                    self.extendedCopy = True
                else:
                    self.finish()

    def finish(self,closed=False):
        if self.running:
            if self.linetrack:
                self.linetrack.finalize()
            if self.ghost:
                self.ghost.finalize()
        Modifier.finish(self)

    def numericRadius(self,rad):
        '''this function gets called by the toolbar when
        valid radius have been entered there'''
        #print("dvec:",self.dvec)
        #print("rad:",rad)
        if self.dvec:
            if isinstance(self.dvec,float):
                if self.mode == "Circle":
                    r1 = self.shape.Edges[0].Curve.Radius
                    r2 = self.ghost.getRadius()
                    if r2 >= r1:
                        rad = r1 + rad
                    else:
                        rad = r1 - rad
                    d = str(rad)
                else:
                    print("Draft.Offset error: Unhandled case")
            else:
                self.dvec.normalize()
                self.dvec.multiply(rad)
                d = DraftVecUtils.toString(self.dvec)
            copymode = False
            occmode = self.ui.occOffset.isChecked()
            if self.ui.isCopy.isChecked():
                copymode = True
            FreeCADGui.addModule("Draft")
            self.commit(translate("draft","Offset"),
                        ['Draft.offset(FreeCAD.ActiveDocument.'+self.sel.Name+','+d+',copy='+str(copymode)+',occ='+str(occmode)+')',
                         'FreeCAD.ActiveDocument.recompute()'])
            self.finish()
        else:
            FreeCAD.Console.PrintError(translate("draft","Offset direction is not defined. Please move the mouse on either side of the object first to indicate a direction")+"/n")


class Stretch(Modifier):
    """The Draft_Stretch FreeCAD command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Stretch',
                'Accel' : "S, H",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Stretch", "Stretch"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Stretch", "Stretches the selected objects")}

    def Activated(self):
        Modifier.Activated(self,"Stretch")
        if self.ui:
            if not FreeCADGui.Selection.getSelection():
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Select an object to stretch")+"\n")
                self.call = self.view.addEventCallback("SoEvent",selectObject)
            else:
                self.proceed()

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        supported = ["Rectangle","Wire","BSpline","BezCurve","Sketch"]
        self.sel = []
        for obj in FreeCADGui.Selection.getSelection():
            if Draft.getType(obj) in supported:
                self.sel.append([obj,FreeCAD.Placement()])
            elif hasattr(obj,"Base"):
                if obj.Base:
                    if Draft.getType(obj.Base) in supported:
                        self.sel.append([obj.Base,obj.Placement])

                    elif Draft.getType(obj.Base) in ["Offset2D","Array"]:
                        base = None
                        if hasattr(obj.Base,"Source") and obj.Base.Source:
                            base = obj.Base.Source
                        elif hasattr(obj.Base,"Base") and obj.Base.Base:
                            base = obj.Base.Base
                        if base:
                            if Draft.getType(base) in supported:
                                self.sel.append([base,obj.Placement.multiply(obj.Base.Placement)])
            elif Draft.getType(obj) in ["Offset2D","Array"]:
                base = None
                if hasattr(obj,"Source") and obj.Source:
                    base = obj.Source
                elif hasattr(obj,"Base") and obj.Base:
                    base = obj.Base
                if base:
                    if Draft.getType(base) in supported:
                        self.sel.append([base,obj.Placement])
        if self.ui and self.sel:
            self.step = 1
            self.refpoint = None
            self.ui.pointUi("Stretch")
            self.ui.extUi()
            self.call = self.view.addEventCallback("SoEvent",self.action)
            self.rectracker = trackers.rectangleTracker(dotted=True,scolor=(0.0,0.0,1.0),swidth=2)
            self.nodetracker = []
            self.displacement = None
            FreeCAD.Console.PrintMessage(translate("draft", "Pick first point of selection rectangle")+"\n")

    def action(self,arg):
        """scene event handler"""
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
        elif arg["Type"] == "SoLocation2Event": #mouse movement detection
            point,ctrlPoint,info = getPoint(self,arg) #,mobile=True) #,noTracker=(self.step < 3))
            if self.step == 2:
                self.rectracker.update(point)
            redraw3DView()
        elif arg["Type"] == "SoMouseButtonEvent":
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):
                if (arg["Position"] == self.pos):
                    # clicked twice on the same point
                    self.finish()
                else:
                    point,ctrlPoint,info = getPoint(self,arg) #,mobile=True) #,noTracker=(self.step < 3))
                    self.addPoint(point)

    def addPoint(self,point):
        if self.step == 1:
            # first rctangle point
            FreeCAD.Console.PrintMessage(translate("draft", "Pick opposite point of selection rectangle")+"\n")
            self.ui.setRelative()
            self.rectracker.setorigin(point)
            self.rectracker.on()
            if self.planetrack:
                self.planetrack.set(point)
            self.step = 2
        elif self.step == 2:
            # second rectangle point
            FreeCAD.Console.PrintMessage(translate("draft", "Pick start point of displacement")+"\n")
            self.rectracker.off()
            nodes = []
            self.ops = []
            for sel in self.sel:
                o = sel[0]
                vispla = sel[1]
                tp = Draft.getType(o)
                if tp in ["Wire","BSpline","BezCurve"]:
                    np = []
                    iso = False
                    for p in o.Points:
                        p = o.Placement.multVec(p)
                        p = vispla.multVec(p)
                        isi = self.rectracker.isInside(p)
                        np.append(isi)
                        if isi:
                            iso = True
                            nodes.append(p)
                    if iso:
                        self.ops.append([o,np])
                elif tp in ["Rectangle"]:
                    p1 = Vector(0,0,0)
                    p2 = Vector(o.Length.Value,0,0)
                    p3 = Vector(o.Length.Value,o.Height.Value,0)
                    p4 = Vector(0,o.Height.Value,0)
                    np = []
                    iso = False
                    for p in [p1,p2,p3,p4]:
                        p = o.Placement.multVec(p)
                        p = vispla.multVec(p)
                        isi = self.rectracker.isInside(p)
                        np.append(isi)
                        if isi:
                            iso = True
                            nodes.append(p)
                    if iso:
                        self.ops.append([o,np])
                elif tp in ["Sketch"]:
                    np = []
                    iso = False
                    for p in o.Shape.Vertexes:
                        p = vispla.multVec(p.Point)
                        isi = self.rectracker.isInside(p)
                        np.append(isi)
                        if isi:
                            iso = True
                            nodes.append(p)
                    if iso:
                        self.ops.append([o,np])
                else:
                    p = o.Placement.Base
                    p = vispla.multVec(p)
                    if self.rectracker.isInside(p):
                        self.ops.append([o])
                        nodes.append(p)
            for n in nodes:
                nt = trackers.editTracker(n,inactive=True)
                nt.on()
                self.nodetracker.append(nt)
            self.step = 3
        elif self.step == 3:
            # first point of displacement line
            FreeCAD.Console.PrintMessage(translate("draft", "Pick end point of displacement")+"\n")
            self.displacement = point
            #print "first point:",point
            self.node = [point]
            self.step = 4
        elif self.step == 4:
            #print "second point:",point
            self.displacement = point.sub(self.displacement)
            self.doStretch()
        if self.point:
            self.ui.redraw()

    def numericInput(self,numx,numy,numz):
        """this function gets called by the toolbar when valid x, y, and z have been entered there"""
        point = Vector(numx,numy,numz)
        self.addPoint(point)

    def finish(self,closed=False):
        if hasattr(self,"rectracker") and self.rectracker:
            self.rectracker.finalize()
        if hasattr(self,"nodetracker") and self.nodetracker:
            for n in self.nodetracker:
                n.finalize()
        Modifier.finish(self)

    def doStretch(self):
        """does the actual stretching"""
        commitops = []
        if self.displacement:
            if self.displacement.Length > 0:
                #print "displacement: ",self.displacement
                for ops in self.ops:
                    tp = Draft.getType(ops[0])
                    localdisp = ops[0].Placement.Rotation.inverted().multVec(self.displacement)
                    if tp in ["Wire","BSpline","BezCurve"]:
                        pts = []
                        for i in range(len(ops[1])):
                            if ops[1][i] == False:
                                pts.append(ops[0].Points[i])
                            else:
                                pts.append(ops[0].Points[i].add(localdisp))
                        pts = str(pts).replace("Vector","FreeCAD.Vector")
                        commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Points="+pts)
                    elif tp in ["Sketch"]:
                        baseverts = [ops[0].Shape.Vertexes[i].Point for i in range(len(ops[1])) if ops[1][i]]
                        for i in range(ops[0].GeometryCount):
                            j = 0
                            while True:
                                try:
                                    p = ops[0].getPoint(i,j)
                                except ValueError:
                                    break
                                else:
                                    p = ops[0].Placement.multVec(p)
                                    r = None
                                    for bv in baseverts:
                                        if DraftVecUtils.isNull(p.sub(bv)):
                                            commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".movePoint("+str(i)+","+str(j)+",FreeCAD."+str(localdisp)+",True)")
                                            r = bv
                                            break
                                    if r:
                                        baseverts.remove(r)
                                    j += 1
                    elif tp in ["Rectangle"]:
                        p1 = Vector(0,0,0)
                        p2 = Vector(ops[0].Length.Value,0,0)
                        p3 = Vector(ops[0].Length.Value,ops[0].Height.Value,0)
                        p4 = Vector(0,ops[0].Height.Value,0)
                        if ops[1] == [False,True,True,False]:
                            optype = 1
                        elif ops[1] == [False,False,True,True]:
                            optype = 2
                        elif ops[1] == [True,False,False,True]:
                            optype = 3
                        elif ops[1] == [True,True,False,False]:
                            optype = 4
                        else:
                            optype = 0
                        #print("length:",ops[0].Length,"height:",ops[0].Height," - ",ops[1]," - ",self.displacement)
                        done = False
                        if optype > 0:
                            v1 = ops[0].Placement.multVec(p2).sub(ops[0].Placement.multVec(p1))
                            a1 = round(self.displacement.getAngle(v1),4)
                            v2 = ops[0].Placement.multVec(p4).sub(ops[0].Placement.multVec(p1))
                            a2 = round(self.displacement.getAngle(v2),4)
                            # check if the displacement is along one of the rectangle directions
                            if a1 == 0:
                                if optype == 1:
                                    if ops[0].Length.Value >= 0:
                                        d = ops[0].Length.Value + self.displacement.Length
                                    else:
                                        d = ops[0].Length.Value - self.displacement.Length
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Length="+str(d))
                                    done = True
                                elif optype == 3:
                                    if ops[0].Length.Value >= 0:
                                        d = ops[0].Length.Value - self.displacement.Length
                                    else:
                                        d = ops[0].Length.Value + self.displacement.Length
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Length="+str(d))
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Placement.Base=FreeCAD."+str(ops[0].Placement.Base.add(self.displacement)))
                                    done = True
                            elif a1 == 3.1416:
                                if optype == 1:
                                    if ops[0].Length.Value >= 0:
                                        d = ops[0].Length.Value - self.displacement.Length
                                    else:
                                        d = ops[0].Length.Value + self.displacement.Length
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Length="+str(d))
                                    done = True
                                elif optype == 3:
                                    if ops[0].Length.Value >= 0:
                                        d = ops[0].Length.Value + self.displacement.Length
                                    else:
                                        d = ops[0].Length.Value - self.displacement.Length
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Length="+str(d))
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Placement.Base=FreeCAD."+str(ops[0].Placement.Base.add(self.displacement)))
                                    done = True
                            elif a2 == 0:
                                if optype == 2:
                                    if ops[0].Height.Value >= 0:
                                        d = ops[0].Height.Value + self.displacement.Length
                                    else:
                                        d = ops[0].Height.Value - self.displacement.Length
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Height="+str(d))
                                    done = True
                                elif optype == 4:
                                    if ops[0].Height.Value >= 0:
                                        d = ops[0].Height.Value - self.displacement.Length
                                    else:
                                        d = ops[0].Height.Value + self.displacement.Length
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Height="+str(d))
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Placement.Base=FreeCAD."+str(ops[0].Placement.Base.add(self.displacement)))
                                    done = True
                            elif a2 == 3.1416:
                                if optype == 2:
                                    if ops[0].Height.Value >= 0:
                                        d = ops[0].Height.Value - self.displacement.Length
                                    else:
                                        d = ops[0].Height.Value + self.displacement.Length
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Height="+str(d))
                                    done = True
                                elif optype == 4:
                                    if ops[0].Height.Value >= 0:
                                        d = ops[0].Height.Value + self.displacement.Length
                                    else:
                                        d = ops[0].Height.Value - self.displacement.Length
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Height="+str(d))
                                    commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Placement.Base=FreeCAD."+str(ops[0].Placement.Base.add(self.displacement)))
                                    done = True
                        if not done:
                            # otherwise create a wire copy and stretch it instead
                            FreeCAD.Console.PrintMessage(translate("draft","Turning one Rectangle into a Wire")+"\n")
                            pts = []
                            opts = [p1,p2,p3,p4]
                            for i in range(4):
                                if ops[1][i] == False:
                                    pts.append(opts[i])
                                else:
                                    pts.append(opts[i].add(self.displacement))
                            pts = str(pts).replace("Vector","FreeCAD.Vector")
                            commitops.append("w = Draft.makeWire("+pts+",closed=True)")
                            commitops.append("Draft.formatObject(w,FreeCAD.ActiveDocument."+ops[0].Name+")")
                            commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".ViewObject.hide()")
                            for par in ops[0].InList:
                                if hasattr(par,"Base") and par.Base == ops[0]:
                                    commitops.append("FreeCAD.ActiveDocument."+par.Name+".Base = w")
                    else:
                        commitops.append("FreeCAD.ActiveDocument."+ops[0].Name+".Placement.Base=FreeCAD."+str(ops[0].Placement.Base.add(self.displacement)))
        if commitops:
            commitops.append("FreeCAD.ActiveDocument.recompute()")
            FreeCADGui.addModule("Draft")
            self.commit(translate("draft","Stretch"),commitops)
        self.finish()

class Join(Modifier):
    '''The Draft_Join FreeCAD command definition.'''

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Join',
                'Accel' : "J, O",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Join", "Join"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Join", "Joins two wires together")}

    def Activated(self):
        Modifier.Activated(self,"Join")
        if not self.ui:
            return
        if not FreeCADGui.Selection.getSelection():
            self.ui.selectUi()
            FreeCAD.Console.PrintMessage(translate("draft", "Select an object to join")+"\n")
            self.call = self.view.addEventCallback("SoEvent",selectObject)
        else:
            self.proceed()

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        if FreeCADGui.Selection.getSelection():
            print(FreeCADGui.Selection.getSelection())
            FreeCADGui.addModule("Draft")
            self.commit(translate("draft","Join"),
                ['Draft.joinWires(FreeCADGui.Selection.getSelection())', 'FreeCAD.ActiveDocument.recompute()'])
        self.finish()

class Split(Modifier):
    '''The Draft_Split FreeCAD command definition.'''

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Split',
                'Accel' : "S, P",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Split", "Split"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Split", "Splits a wire into two wires")}

    def Activated(self):
        Modifier.Activated(self,"Split")
        if not self.ui:
            return
        FreeCAD.Console.PrintMessage(translate("draft", "Select an object to split")+"\n")
        self.call = self.view.addEventCallback("SoEvent", self.action)

    def action(self, arg):
        "scene event handler"
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
        elif arg["Type"] == "SoLocation2Event":
            getPoint(self, arg)
            redraw3DView()
        elif arg["Type"] == "SoMouseButtonEvent" and arg["State"] == "DOWN" and arg["Button"] == "BUTTON1":
            self.point, ctrlPoint, info = getPoint(self, arg)
            if "Edge" in info["Component"]:
                return self.proceed(info)

    def proceed(self, info):
        Draft.split(FreeCAD.ActiveDocument.getObject(info["Object"]),
            self.point, int(info["Component"][4:]))
        if self.call:
            self.view.removeEventCallback("SoEvent", self.call)
        self.finish()

class Upgrade(Modifier):
    '''The Draft_Upgrade FreeCAD command definition.'''

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Upgrade',
                'Accel' : "U, P",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Upgrade", "Upgrade"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Upgrade", "Joins the selected objects into one, or converts closed wires to filled faces, or unites faces")}

    def Activated(self):
        Modifier.Activated(self,"Upgrade")
        if self.ui:
            if not FreeCADGui.Selection.getSelection():
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Select an object to upgrade")+"\n")
                self.call = self.view.addEventCallback("SoEvent",selectObject)
            else:
                self.proceed()

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        if FreeCADGui.Selection.getSelection():
            FreeCADGui.addModule("Draft")
            self.commit(translate("draft","Upgrade"),
                        ['Draft.upgrade(FreeCADGui.Selection.getSelection(),delete=True)',
                         'FreeCAD.ActiveDocument.recompute()'])
        self.finish()


class Downgrade(Modifier):
    '''The Draft_Downgrade FreeCAD command definition.'''

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Downgrade',
                'Accel' : "D, N",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Downgrade", "Downgrade"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Downgrade", "Explodes the selected objects into simpler objects, or subtracts faces")}

    def Activated(self):
        Modifier.Activated(self,"Downgrade")
        if self.ui:
            if not FreeCADGui.Selection.getSelection():
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Select an object to upgrade")+"\n")
                self.call = self.view.addEventCallback("SoEvent",selectObject)
            else:
                self.proceed()

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        if FreeCADGui.Selection.getSelection():
            FreeCADGui.addModule("Draft")
            self.commit(translate("draft","Downgrade"),
                        ['Draft.downgrade(FreeCADGui.Selection.getSelection(),delete=True)',
                         'FreeCAD.ActiveDocument.recompute()'])
        self.finish()

class Trimex(Modifier):
    """The Draft_Trimex FreeCAD command definition.
    This tool trims or extends lines, wires and arcs,
    or extrudes single faces. SHIFT constrains to the last point
    or extrudes in direction to the face normal."""

    def GetResources(self):
        return {'Pixmap' : 'Draft_Trimex',
                'Accel' : "T, R",
                'MenuText' : QtCore.QT_TRANSLATE_NOOP("Draft_Trimex", "Trimex"),
                'ToolTip' : QtCore.QT_TRANSLATE_NOOP("Draft_Trimex", "Trims or extends the selected object, or extrudes single faces. CTRL snaps, SHIFT constrains to current segment or to normal, ALT inverts")}

    def Activated(self):
        Modifier.Activated(self,"Trimex")
        self.edges = []
        self.placement = None
        self.ghost = []
        self.linetrack = None
        self.color = None
        self.width = None
        if self.ui:
            if not FreeCADGui.Selection.getSelection():
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Select object(s) to trim/extend")+"\n")
                self.call = self.view.addEventCallback("SoEvent",selectObject)
            else:
                self.proceed()

    def proceed(self):
        if self.call: self.view.removeEventCallback("SoEvent",self.call)
        sel = FreeCADGui.Selection.getSelection()
        if len(sel) == 2:
            self.trimObjects(sel)
            self.finish()
            return
        self.obj = sel[0]
        self.ui.trimUi()
        self.linetrack = trackers.lineTracker()

        import DraftGeomUtils
        import Part

        if not "Shape" in self.obj.PropertiesList: return
        if "Placement" in self.obj.PropertiesList:
            self.placement = self.obj.Placement
        if len(self.obj.Shape.Faces) == 1:
            # simple extrude mode, the object itself is extruded
            self.extrudeMode = True
            self.ghost = [trackers.ghostTracker([self.obj])]
            self.normal = self.obj.Shape.Faces[0].normalAt(.5,.5)
            for v in self.obj.Shape.Vertexes:
                self.ghost.append(trackers.lineTracker())
        elif len(self.obj.Shape.Faces) > 1:
            # face extrude mode, a new object is created
            ss =  FreeCADGui.Selection.getSelectionEx()[0]
            if len(ss.SubObjects) == 1:
                if ss.SubObjects[0].ShapeType == "Face":
                    self.obj = self.doc.addObject("Part::Feature","Face")
                    self.obj.Shape = ss.SubObjects[0]
                    self.extrudeMode = True
                    self.ghost = [trackers.ghostTracker([self.obj])]
                    self.normal = self.obj.Shape.Faces[0].normalAt(.5,.5)
                    for v in self.obj.Shape.Vertexes:
                        self.ghost.append(trackers.lineTracker())
        else:
            # normal wire trimex mode
            self.color = self.obj.ViewObject.LineColor
            self.width = self.obj.ViewObject.LineWidth
            #self.obj.ViewObject.Visibility = False
            self.obj.ViewObject.LineColor = (.5,.5,.5)
            self.obj.ViewObject.LineWidth = 1
            self.extrudeMode = False
            if self.obj.Shape.Wires:
                self.edges = self.obj.Shape.Wires[0].Edges
                self.edges = Part.__sortEdges__(self.edges)
            else:
                self.edges = self.obj.Shape.Edges
            self.ghost = []
            lc = self.color
            sc = (lc[0],lc[1],lc[2])
            sw = self.width
            for e in self.edges:
                if DraftGeomUtils.geomType(e) == "Line":
                    self.ghost.append(trackers.lineTracker(scolor=sc,swidth=sw))
                else:
                    self.ghost.append(trackers.arcTracker(scolor=sc,swidth=sw))
        if not self.ghost: self.finish()
        for g in self.ghost: g.on()
        self.activePoint = 0
        self.nodes = []
        self.shift = False
        self.alt = False
        self.force = None
        self.cv = None
        self.call = self.view.addEventCallback("SoEvent",self.action)
        FreeCAD.Console.PrintMessage(translate("draft", "Pick distance")+"\n")

    def action(self,arg):
        """scene event handler"""
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
        elif arg["Type"] == "SoLocation2Event": #mouse movement detection
            self.shift = hasMod(arg,MODCONSTRAIN)
            self.alt = hasMod(arg,MODALT)
            self.ctrl = hasMod(arg,MODSNAP)
            if self.extrudeMode:
                arg["ShiftDown"] = False
            elif hasattr(FreeCADGui,"Snapper"):
                FreeCADGui.Snapper.setSelectMode(not self.ctrl)
            wp = not(self.extrudeMode and self.shift)
            self.point,cp,info = getPoint(self,arg,workingplane=wp)
            if hasMod(arg,MODSNAP): self.snapped = None
            else: self.snapped = self.view.getObjectInfo((arg["Position"][0],arg["Position"][1]))
            if self.extrudeMode:
                dist = self.extrude(self.shift)
            else:
                dist = self.redraw(self.point,self.snapped,self.shift,self.alt)
            self.ui.setRadiusValue(dist,unit="Length")
            self.ui.radiusValue.setFocus()
            self.ui.radiusValue.selectAll()
            redraw3DView()

        elif arg["Type"] == "SoMouseButtonEvent":
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):
                cursor = arg["Position"]
                self.shift = hasMod(arg,MODCONSTRAIN)
                self.alt = hasMod(arg,MODALT)
                if hasMod(arg,MODSNAP): self.snapped = None
                else: self.snapped = self.view.getObjectInfo((cursor[0],cursor[1]))
                self.trimObject()
                self.finish()

    def extrude(self,shift=False,real=False):
        """redraws the ghost in extrude mode"""
        self.newpoint = self.obj.Shape.Faces[0].CenterOfMass
        dvec = self.point.sub(self.newpoint)
        if not shift: delta = DraftVecUtils.project(dvec,self.normal)
        else: delta = dvec
        if self.force and delta.Length:
            ratio = self.force/delta.Length
            delta.multiply(ratio)
        if real: return delta
        self.ghost[0].trans.translation.setValue([delta.x,delta.y,delta.z])
        for i in range(1,len(self.ghost)):
            base = self.obj.Shape.Vertexes[i-1].Point
            self.ghost[i].p1(base)
            self.ghost[i].p2(base.add(delta))
        return delta.Length

    def redraw(self,point,snapped=None,shift=False,alt=False,real=None):
        """redraws the ghost"""

        # initializing
        reverse = False
        for g in self.ghost: g.off()
        if real: newedges = []

        import DraftGeomUtils
        import Part

        # finding the active point
        vlist = []
        for e in self.edges: vlist.append(e.Vertexes[0].Point)
        vlist.append(self.edges[-1].Vertexes[-1].Point)
        if shift: npoint = self.activePoint
        else: npoint = DraftGeomUtils.findClosest(point,vlist)
        if npoint > len(self.edges)/2: reverse = True
        if alt: reverse = not reverse
        self.activePoint = npoint

        # sorting out directions
        if reverse and (npoint > 0): npoint = npoint-1
        if (npoint > len(self.edges)-1):
            edge = self.edges[-1]
            ghost = self.ghost[-1]
        else:
            edge = self.edges[npoint]
            ghost = self.ghost[npoint]
        if reverse:
            v1 = edge.Vertexes[-1].Point
            v2 = edge.Vertexes[0].Point
        else:
            v1 = edge.Vertexes[0].Point
            v2 = edge.Vertexes[-1].Point

        # snapping
        if snapped:
            snapped = self.doc.getObject(snapped['Object'])
            if hasattr(snapped,"Shape"):
                pts = []
                for e in snapped.Shape.Edges:
                    int = DraftGeomUtils.findIntersection(edge,e,True,True)
                    if int: pts.extend(int)
                if pts:
                    point = pts[DraftGeomUtils.findClosest(point,pts)]

        # modifying active edge
        if DraftGeomUtils.geomType(edge) == "Line":
            ve = DraftGeomUtils.vec(edge)
            chord = v1.sub(point)
            n = ve.cross(chord)
            if n.Length == 0:
                self.newpoint = point
            else:
                perp = ve.cross(n)
                proj = DraftVecUtils.project(chord,perp)
                self.newpoint = Vector.add(point,proj)
            dist = v1.sub(self.newpoint).Length
            ghost.p1(self.newpoint)
            ghost.p2(v2)
            self.ui.labelRadius.setText(translate("draft","Distance"))
            self.ui.radiusValue.setToolTip(translate("draft", "The offset distance"))
            if real:
                if self.force:
                    ray = self.newpoint.sub(v1)
                    ray.multiply(self.force/ray.Length)
                    self.newpoint = Vector.add(v1,ray)
                newedges.append(Part.LineSegment(self.newpoint,v2).toShape())
        else:
            center = edge.Curve.Center
            rad = edge.Curve.Radius
            ang1 = DraftVecUtils.angle(v2.sub(center))
            ang2 = DraftVecUtils.angle(point.sub(center))
            self.newpoint=Vector.add(center,DraftVecUtils.rotate(Vector(rad,0,0),-ang2))
            self.ui.labelRadius.setText(translate("draft","Angle"))
            self.ui.radiusValue.setToolTip(translate("draft", "The offset angle"))
            dist = math.degrees(-ang2)
            # if ang1 > ang2: ang1,ang2 = ang2,ang1
            #print("last calculated:",math.degrees(-ang1),math.degrees(-ang2))
            ghost.setEndAngle(-ang2)
            ghost.setStartAngle(-ang1)
            ghost.setCenter(center)
            ghost.setRadius(rad)
            if real:
                if self.force:
                    angle = math.radians(self.force)
                    newray = DraftVecUtils.rotate(Vector(rad,0,0),-angle)
                    self.newpoint = Vector.add(center,newray)
                chord = self.newpoint.sub(v2)
                perp = chord.cross(Vector(0,0,1))
                scaledperp = DraftVecUtils.scaleTo(perp,rad)
                midpoint = Vector.add(center,scaledperp)
                newedges.append(Part.Arc(self.newpoint,midpoint,v2).toShape())
        ghost.on()

        # resetting the visible edges
        if not reverse:
            li = list(range(npoint+1,len(self.edges)))
        else:
            li = list(range(npoint-1,-1,-1))
        for i in li:
            edge = self.edges[i]
            ghost = self.ghost[i]
            if DraftGeomUtils.geomType(edge) == "Line":
                ghost.p1(edge.Vertexes[0].Point)
                ghost.p2(edge.Vertexes[-1].Point)
            else:
                ang1 = DraftVecUtils.angle(edge.Vertexes[0].Point.sub(center))
                ang2 = DraftVecUtils.angle(edge.Vertexes[-1].Point.sub(center))
                # if ang1 > ang2: ang1,ang2 = ang2,ang1
                ghost.setEndAngle(-ang2)
                ghost.setStartAngle(-ang1)
                ghost.setCenter(edge.Curve.Center)
                ghost.setRadius(edge.Curve.Radius)
            if real: newedges.append(edge)
            ghost.on()

        # finishing
        if real: return newedges
        else: return dist

    def trimObject(self):
        """trims the actual object"""
        import Part
        if self.extrudeMode:
            delta = self.extrude(self.shift,real=True)
            #print("delta",delta)
            self.doc.openTransaction("Extrude")
            obj = Draft.extrude(self.obj,delta,solid=True)
            self.doc.commitTransaction()
            self.obj = obj
        else:
            edges = self.redraw(self.point,self.snapped,self.shift,self.alt,real=True)
            newshape = Part.Wire(edges)
            self.doc.openTransaction("Trim/extend")
            if Draft.getType(self.obj) in ["Wire","BSpline"]:
                p = []
                if self.placement:
                    invpl = self.placement.inverse()
                for v in newshape.Vertexes:
                    np = v.Point
                    if self.placement:
                        np = invpl.multVec(np)
                    p.append(np)
                self.obj.Points = p
            elif Draft.getType(self.obj) == "Part::Line":
                p = []
                if self.placement:
                    invpl = self.placement.inverse()
                for v in newshape.Vertexes:
                    np = v.Point
                    if self.placement:
                        np = invpl.multVec(np)
                    p.append(np)
                if ((p[0].x == self.obj.X1) and (p[0].y == self.obj.Y1) and (p[0].z == self.obj.Z1)):
                    self.obj.X2 = p[-1].x
                    self.obj.Y2 = p[-1].y
                    self.obj.Z2 = p[-1].z
                elif ((p[-1].x == self.obj.X1) and (p[-1].y == self.obj.Y1) and (p[-1].z == self.obj.Z1)):
                    self.obj.X2 = p[0].x
                    self.obj.Y2 = p[0].y
                    self.obj.Z2 = p[0].z
                elif ((p[0].x == self.obj.X2) and (p[0].y == self.obj.Y2) and (p[0].z == self.obj.Z2)):
                    self.obj.X1 = p[-1].x
                    self.obj.Y1 = p[-1].y
                    self.obj.Z1 = p[-1].z
                else:
                    self.obj.X1 = p[0].x
                    self.obj.Y1 = p[0].y
                    self.obj.Z1 = p[0].z
            elif Draft.getType(self.obj) == "Circle":
                angles = self.ghost[0].getAngles()
                #print("original",self.obj.FirstAngle," ",self.obj.LastAngle)
                #print("new",angles)
                if angles[0] > angles[1]: angles = (angles[1],angles[0])
                self.obj.FirstAngle = angles[0]
                self.obj.LastAngle = angles[1]
            else:
                self.obj.Shape = newshape
            self.doc.commitTransaction()
        self.doc.recompute()
        for g in self.ghost: g.off()

    def trimObjects(self,objectslist):
        """attempts to trim two objects together"""
        import Part
        import DraftGeomUtils
        wires = []
        for obj in objectslist:
            if not Draft.getType(obj) in ["Wire","Circle"]:
                FreeCAD.Console.PrintError(translate("draft","Unable to trim these objects, only Draft wires and arcs are supported")+"\n")
                return
            if len (obj.Shape.Wires) > 1:
                FreeCAD.Console.PrintError(translate("draft","Unable to trim these objects, too many wires")+"\n")
                return
            if len(obj.Shape.Wires) == 1:
                wires.append(obj.Shape.Wires[0])
            else:
                wires.append(Part.Wire(obj.Shape.Edges))
        ints = []
        edge1 = None
        edge2 = None
        for i1,e1 in enumerate(wires[0].Edges):
            for i2,e2 in enumerate(wires[1].Edges):
                i = DraftGeomUtils.findIntersection(e1,e2,dts=False)
                if len(i) == 1:
                    ints.append(i[0])
                    edge1 = i1
                    edge2 = i2
        if not ints:
            FreeCAD.Console.PrintErro(translate("draft","These objects don't intersect")+"\n")
            return
        if len(ints) != 1:
            FreeCAD.Console.PrintError(translate("draft","Too many intersection points")+"\n")
            return
        v11 = wires[0].Vertexes[0].Point
        v12 = wires[0].Vertexes[-1].Point
        v21 = wires[1].Vertexes[0].Point
        v22 = wires[1].Vertexes[-1].Point
        if DraftVecUtils.closest(ints[0],[v11,v12]) == 1:
            last1 = True
        else:
            last1 = False
        if DraftVecUtils.closest(ints[0],[v21,v22]) == 1:
            last2 = True
        else:
            last2 = False
        for i,obj in enumerate(objectslist):
            if i == 0:
                ed = edge1
                la = last1
            else:
                ed = edge2
                la = last2
            if Draft.getType(obj) == "Wire":
                if la:
                    pts = obj.Points[:ed+1] + ints
                else:
                    pts = ints + obj.Points[ed+1:]
                obj.Points = pts
            else:
                vec = ints[0].sub(obj.Placement.Base)
                vec = obj.Placement.inverse().Rotation.multVec(vec)
                ang = math.degrees(-DraftVecUtils.angle(vec,obj.Placement.Rotation.multVec(FreeCAD.Vector(1,0,0)),obj.Shape.Edges[0].Curve.Axis))
                if la:
                    obj.LastAngle = ang
                else:
                    obj.FirstAngle = ang
        self.doc.recompute()


    def finish(self,closed=False):
        Modifier.finish(self)
        self.force = None
        if self.ui:
            if self.linetrack:
                self.linetrack.finalize()
            if self.ghost:
                for g in self.ghost:
                    g.finalize()
            if self.obj:
                self.obj.ViewObject.Visibility = True
                if self.color:
                    self.obj.ViewObject.LineColor = self.color
                if self.width:
                    self.obj.ViewObject.LineWidth = self.width
            Draft.select(self.obj)

    def numericRadius(self,dist):
        """this function gets called by the toolbar when valid distance have been entered there"""
        self.force = dist
        self.trimObject()
        self.finish()


class Scale(Modifier):
    '''The Draft_Scale FreeCAD command definition.
    This tool scales the selected objects from a base point.'''

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Scale',
                'Accel' : "S, C",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Scale", "Scale"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Scale", "Scales the selected objects from a base point. CTRL to snap, SHIFT to constrain, ALT to copy")}

    def Activated(self):
        self.name = translate("draft","Scale", utf8_decode=True)
        Modifier.Activated(self,self.name)
        if not self.ui:
            return
        self.ghosts = []
        self.get_object_selection()

    def get_object_selection(self):
        if FreeCADGui.Selection.getSelection():
            return self.proceed()
        self.ui.selectUi()
        FreeCAD.Console.PrintMessage(translate("draft", "Select an object to scale")+"\n")
        self.call = self.view.addEventCallback("SoEvent",selectObject)

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent", self.call)
        self.selected_objects = FreeCADGui.Selection.getSelection()
        self.selected_objects = Draft.getGroupContents(self.selected_objects)
        self.selected_subelements = FreeCADGui.Selection.getSelectionEx()
        self.refs = []
        self.ui.pointUi(self.name)
        self.ui.modUi()
        self.ui.xValue.setFocus()
        self.ui.xValue.selectAll()
        self.pickmode = False
        self.task = None
        self.call = self.view.addEventCallback("SoEvent", self.action)
        FreeCAD.Console.PrintMessage(translate("draft", "Pick base point")+"\n")

    def set_ghosts(self):
        if self.ui.isSubelementMode.isChecked():
            return self.set_subelement_ghosts()
        self.ghosts = [trackers.ghostTracker(self.selected_objects)]

    def set_subelement_ghosts(self):
        import Part
        for object in self.selected_subelements:
            for subelement in object.SubObjects:
                if isinstance(subelement, Part.Vertex) \
                    or isinstance(subelement, Part.Edge):
                    self.ghosts.append(trackers.ghostTracker(subelement))

    def pickRef(self):
        self.pickmode = True
        if self.node:
            self.node = self.node[:1] # remove previous picks
        FreeCAD.Console.PrintMessage(translate("draft", "Pick reference distance from base point")+"\n")
        self.call = self.view.addEventCallback("SoEvent",self.action)

    def action(self,arg):
        """scene event handler"""
        if arg["Type"] == "SoKeyboardEvent" and arg["Key"] == "ESCAPE":
            self.finish()
        elif arg["Type"] == "SoLocation2Event":
            self.handle_mouse_move_event(arg)
        elif arg["Type"] == "SoMouseButtonEvent" \
            and arg["State"] == "DOWN" \
            and (arg["Button"] == "BUTTON1") \
            and self.point:
            self.handle_mouse_click_event()

    def handle_mouse_move_event(self, arg):
        for ghost in self.ghosts:
            ghost.off()
        self.point, ctrlPoint, info = getPoint(self, arg, sym=True)

    def handle_mouse_click_event(self):
        if not self.ghosts:
            self.set_ghosts()
        self.numericInput(self.point.x, self.point.y, self.point.z)

    def scale(self):
        self.delta = Vector(self.task.xValue.value(), self.task.yValue.value(), self.task.zValue.value())
        self.center = self.node[0]
        if self.task.isSubelementMode.isChecked():
            self.scale_subelements()
        elif self.task.isClone.isChecked():
            self.scale_with_clone()
        else:
            self.scale_object()
        self.finish()

    def scale_subelements(self):
        try:
            if self.task.isCopy.isChecked():
                self.commit(translate("draft", "Copy"), self.build_copy_subelements_command())
            else:
                self.commit(translate("draft", "Scale"), self.build_scale_subelements_command())
        except:
            FreeCAD.Console.PrintError(translate("draft", "Some subelements could not be scaled."))

    def scale_with_clone(self):
        if self.task.relative.isChecked():
            self.delta = FreeCAD.DraftWorkingPlane.getGlobalCoords(self.delta)
        objects = '[' + ','.join(['FreeCAD.ActiveDocument.' + object.Name for object in self.selected_objects]) + ']'
        FreeCADGui.addModule("Draft")
        self.commit(translate("draft","Copy") if self.task.isCopy.isChecked() else translate("draft","Scale"),
                    ['clone = Draft.clone('+objects+',forcedraft=True)',
                     'clone.Scale = '+DraftVecUtils.toString(self.delta),
                     'FreeCAD.ActiveDocument.recompute()'])

    def build_copy_subelements_command(self):
        import Part
        command = []
        arguments = []
        for object in self.selected_subelements:
            for index, subelement in enumerate(object.SubObjects):
                if not isinstance(subelement, Part.Edge):
                    continue
                arguments.append('[FreeCAD.ActiveDocument.{}, {}, {}, {}]'.format(
                    object.ObjectName,
                    int(object.SubElementNames[index][len("Edge"):])-1,
                    DraftVecUtils.toString(self.delta),
                    DraftVecUtils.toString(self.center)))
        command.append('Draft.copyScaledEdges([{}])'.format(','.join(arguments)))
        command.append('FreeCAD.ActiveDocument.recompute()')
        return command

    def build_scale_subelements_command(self):
        import Part
        command = []
        for object in self.selected_subelements:
            for index, subelement in enumerate(object.SubObjects):
                if isinstance(subelement, Part.Vertex):
                    command.append('Draft.scaleVertex(FreeCAD.ActiveDocument.{}, {}, {}, {})'.format(
                        object.ObjectName,
                        int(object.SubElementNames[index][len("Vertex"):])-1,
                        DraftVecUtils.toString(self.delta),
                        DraftVecUtils.toString(self.center)))
                elif isinstance(subelement, Part.Edge):
                    command.append('Draft.scaleEdge(FreeCAD.ActiveDocument.{}, {}, {}, {})'.format(
                        object.ObjectName,
                        int(object.SubElementNames[index][len("Edge"):])-1,
                        DraftVecUtils.toString(self.delta),
                        DraftVecUtils.toString(self.center)))
        command.append('FreeCAD.ActiveDocument.recompute()')
        return command
    
    def is_scalable(self,obj):
        t = Draft.getType(obj)
        if t in ["Rectangle","Wire","Annotation","BSpline"]:
            # TODO - support more types in Draft.scale
            return True
        else:
            return False

    def scale_object(self):
        if self.task.relative.isChecked():
            self.delta = FreeCAD.DraftWorkingPlane.getGlobalCoords(self.delta)
        goods = []
        bads = []
        for obj in self.selected_objects:
            if self.is_scalable(obj):
                goods.append(obj)
            else:
                bads.append(obj)
        if bads:
            if len(bads) == 1:
                m = translate("draft","Unable to scale object")+": "+bads[0].Label
            else:
                m = translate("draft","Unable to scale objects")+": "+",".join([o.Label for o in bads])
            m += " - "+translate("draft","This object type cannot be scaled directly. Please use the clone method.")+"\n"
            FreeCAD.Console.PrintError(m)
        if goods:
            objects = '[' + ','.join(['FreeCAD.ActiveDocument.' + obj.Name for obj in goods]) + ']'
            FreeCADGui.addModule("Draft")
            self.commit(translate("draft","Copy" if self.task.isCopy.isChecked() else "Scale"),
                        ['Draft.scale('+objects+',scale='+DraftVecUtils.toString(self.delta)+',center='+DraftVecUtils.toString(self.center)+',copy='+str(self.task.isCopy.isChecked())+')',
                         'FreeCAD.ActiveDocument.recompute()'])

    def scaleGhost(self,x,y,z,rel):
        delta = Vector(x,y,z)
        if rel:
            delta = FreeCAD.DraftWorkingPlane.getGlobalCoords(delta)
        for ghost in self.ghosts:
            ghost.scale(delta)
        # calculate a correction factor depending on the scaling center
        corr = Vector(self.node[0].x,self.node[0].y,self.node[0].z)
        corr.scale(delta.x,delta.y,delta.z)
        corr = (corr.sub(self.node[0])).negative()
        for ghost in self.ghosts:
            ghost.move(corr)
            ghost.on()

    def numericInput(self,numx,numy,numz):
        """this function gets called by the toolbar when a valid base point has been entered"""
        self.point = Vector(numx,numy,numz)
        self.node.append(self.point)
        if not self.pickmode:
            if not self.ghosts:
                self.set_ghosts()
            self.ui.offUi()
            if self.call:
                self.view.removeEventCallback("SoEvent",self.call)
            self.task = task_scale.ScaleTaskPanel()
            self.task.sourceCmd = self
            ToDo.delay(FreeCADGui.Control.showDialog, self.task)
            ToDo.delay(self.task.xValue.selectAll, None)
            ToDo.delay(self.task.xValue.setFocus, None)
            for ghost in self.ghosts:
                ghost.on()
        elif len(self.node) == 2:
            FreeCAD.Console.PrintMessage(translate("draft", "Pick new distance from base point")+"\n")
        elif len(self.node) == 3:
            if hasattr(FreeCADGui,"Snapper"):
                FreeCADGui.Snapper.off()
            if self.call:
                self.view.removeEventCallback("SoEvent",self.call)
            d1 = (self.node[1].sub(self.node[0])).Length
            d2 = (self.node[2].sub(self.node[0])).Length
            #print d2,"/",d1,"=",d2/d1
            if hasattr(self,"task"):
                if self.task:
                    self.task.lock.setChecked(True)
                    self.task.setValue(d2/d1)

    def finish(self,closed=False,cont=False):
        Modifier.finish(self)
        for ghost in self.ghosts:
            ghost.finalize()


class Drawing(Modifier):
    """The Draft Drawing command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Drawing',
                'Accel' : "D, D",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Drawing", "Drawing"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Drawing", "Puts the selected objects on a Drawing sheet")}

    def Activated(self):
        Modifier.Activated(self,"Drawing")
        if not FreeCADGui.Selection.getSelection():
            self.ghost = None
            self.ui.selectUi()
            FreeCAD.Console.PrintMessage(translate("draft", "Select an object to project")+"\n")
            self.call = self.view.addEventCallback("SoEvent",selectObject)
        else:
            self.proceed()

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        sel = FreeCADGui.Selection.getSelection()
        if not sel:
            self.page = self.createDefaultPage()
        else:
            self.page = None
            # if the user selected a page, put the objects on that page
            for obj in sel:
                if obj.isDerivedFrom("Drawing::FeaturePage"):
                    self.page = obj
                    break
            if not self.page:
                # no page selected, default to the first page in the document
                for obj in self.doc.Objects:
                    if obj.isDerivedFrom("Drawing::FeaturePage"):
                        self.page = obj
                        break
            if not self.page:
                # no page in the document, create a default page.
                self.page = self.createDefaultPage()
            otherProjection = None
            # if an existing projection is selected, reuse its projection properties
            for obj in sel:
                if obj.isDerivedFrom("Drawing::FeatureView"):
                    otherProjection = obj
                    break
            sel.reverse()
            for obj in sel:
                if ( obj.ViewObject.isVisible() and not obj.isDerivedFrom("Drawing::FeatureView")
                        and not obj.isDerivedFrom("Drawing::FeaturePage") ):
                    name = 'View'+obj.Name
                    # no reason to remove the old one...
                    #oldobj = self.page.getObject(name)
                    #if oldobj:
                    #    self.doc.removeObject(oldobj.Name)
                    Draft.makeDrawingView(obj,self.page,otherProjection=otherProjection)
            self.doc.recompute()

    def createDefaultPage(self):
        """created a default page"""
        template = Draft.getParam("template",FreeCAD.getResourceDir()+'Mod/Drawing/Templates/A3_Landscape.svg')
        page = self.doc.addObject('Drawing::FeaturePage','Page')
        page.ViewObject.HintOffsetX = 200
        page.ViewObject.HintOffsetY = 100
        page.ViewObject.HintScale = 20
        page.Template = template
        self.doc.recompute()
        return page


class SubelementHighlight(Modifier):
    """The Draft_SubelementHighlight FreeCAD command definition"""

    def __init__(self):
        self.is_running = False
        self.editable_objects = []
        self.original_view_settings = {}

    def GetResources(self):
        return {'Pixmap'  : 'Draft_SubelementHighlight',
                'Accel' : "H, S",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_SubelementHighlight", "Subelement highlight"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_SubelementHighlight",
                                                    "Highlight the subelements "
                                                    "of the selected objects, "
                                                    "so that they can then be edited "
                                                    "with the move, rotate, and scale tools")}

    def Activated(self):
        if self.is_running:
            return self.finish()
        self.is_running = True
        Modifier.Activated(self, "SubelementHighlight")
        self.get_selection()

    def proceed(self):
        self.remove_view_callback()
        self.get_editable_objects_from_selection()
        if not self.editable_objects:
            return self.finish()
        self.call = self.view.addEventCallback("SoEvent", self.action)
        self.highlight_editable_objects()

    def finish(self):
        Modifier.finish(self)
        self.remove_view_callback()
        self.restore_editable_objects_graphics()
        self.__init__()

    def action(self, event):
        if event["Type"] == "SoKeyboardEvent" and event["Key"] == "ESCAPE":
            self.finish()

    def get_selection(self):
        if not FreeCADGui.Selection.getSelection() and self.ui:
            FreeCAD.Console.PrintMessage(translate("draft", "Select an object to edit")+"\n")
            self.call = self.view.addEventCallback("SoEvent", selectObject)
        else:
            self.proceed()

    def remove_view_callback(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)

    def get_editable_objects_from_selection(self):
        for object in FreeCADGui.Selection.getSelection():
            if object.isDerivedFrom("Part::Part2DObject"):
                self.editable_objects.append(object)
            elif hasattr(object, "Base") and object.Base.isDerivedFrom("Part::Part2DObject"):
                self.editable_objects.append(object.Base)

    def highlight_editable_objects(self):
        for object in self.editable_objects:
            self.original_view_settings[object.Name] = {
                'Visibility': object.ViewObject.Visibility,
                'PointSize': object.ViewObject.PointSize,
                'PointColor': object.ViewObject.PointColor,
                'LineColor': object.ViewObject.LineColor
            }
            object.ViewObject.Visibility = True
            object.ViewObject.PointSize = 10
            object.ViewObject.PointColor = (1., 0., 0.)
            object.ViewObject.LineColor = (1., 0., 0.)
            xray = coin.SoAnnotation()
            xray.addChild(object.ViewObject.RootNode.getChild(2).getChild(0))
            xray.setName("xray")
            object.ViewObject.RootNode.addChild(xray)

    def restore_editable_objects_graphics(self):
        for object in self.editable_objects:
            try:
                for attribute, value in self.original_view_settings[object.Name].items():
                    view_object = object.ViewObject
                    setattr(view_object, attribute, value)
                    view_object.RootNode.removeChild(view_object.RootNode.getByName("xray"))
            except:
                # This can occur if objects have had graph changing operations
                pass


class WireToBSpline(Modifier):
    """The Draft_Wire2BSpline FreeCAD command definition"""

    def __init__(self):
        self.running = False

    def GetResources(self):
        return {'Pixmap'  : 'Draft_WireToBSpline',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_WireToBSpline", "Wire to B-spline"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_WireToBSpline", "Converts between Wire and B-spline")}

    def IsActive(self):
        if FreeCADGui.Selection.getSelection():
            return True
        else:
            return False

    def Activated(self):
        if self.running:
            self.finish()
        else:
            selection = FreeCADGui.Selection.getSelection()
            if selection:
                if (Draft.getType(selection[0]) in ['Wire','BSpline']):
                    Modifier.Activated(self,"Convert Curve Type")
                    if self.doc:
                        self.obj = FreeCADGui.Selection.getSelection()
                        if self.obj:
                            self.obj = self.obj[0]
                            self.pl = None
                            if "Placement" in self.obj.PropertiesList:
                                self.pl = self.obj.Placement
                            self.Points = self.obj.Points
                            self.closed = self.obj.Closed
                            n = None
                            if (Draft.getType(self.obj) == 'Wire'):
                                n = Draft.makeBSpline(self.Points, self.closed, self.pl)
                            elif (Draft.getType(self.obj) == 'BSpline'):
                                self.bs2wire = True
                                n = Draft.makeWire(self.Points, self.closed, self.pl, None, None, self.bs2wire)
                            if n:
                                Draft.formatObject(n,self.obj)
                                self.doc.recompute()
                        else:
                            self.finish()


class Shape2DView(Modifier):
    """The Shape2DView FreeCAD command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Draft_2DShapeView',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Shape2DView", "Shape 2D view"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Shape2DView", "Creates Shape 2D views of selected objects")}

    def Activated(self):
        Modifier.Activated(self)
        if not FreeCADGui.Selection.getSelection():
            if self.ui:
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Select an object to project")+"\n")
                self.call = self.view.addEventCallback("SoEvent",selectObject)
        else:
            self.proceed()

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        faces = []
        objs = []
        vec = FreeCADGui.ActiveDocument.ActiveView.getViewDirection().negative()
        sel = FreeCADGui.Selection.getSelectionEx()
        for s in sel:
            objs.append(s.Object)
            for e in s.SubElementNames:
                if "Face" in e:
                    faces.append(int(e[4:])-1)
        #print(objs,faces)
        commitlist = []
        FreeCADGui.addModule("Draft")
        if (len(objs) == 1) and faces:
            commitlist.append("Draft.makeShape2DView(FreeCAD.ActiveDocument."+objs[0].Name+",FreeCAD.Vector"+str(tuple(vec))+",facenumbers="+str(faces)+")")
        else:
            for o in objs:
                commitlist.append("Draft.makeShape2DView(FreeCAD.ActiveDocument."+o.Name+",FreeCAD.Vector"+str(tuple(vec))+")")
        if commitlist:
            commitlist.append("FreeCAD.ActiveDocument.recompute()")
            self.commit(translate("draft","Create 2D view"),commitlist)
        self.finish()


class Draft2Sketch(Modifier):
    """The Draft2Sketch FreeCAD command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Draft2Sketch',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Draft2Sketch", "Draft to Sketch"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Draft2Sketch", "Convert bidirectionally between Draft and Sketch objects")}

    def Activated(self):
        Modifier.Activated(self)
        if not FreeCADGui.Selection.getSelection():
            if self.ui:
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Select an object to convert")+"\n")
                self.call = self.view.addEventCallback("SoEvent",selectObject)
        else:
            self.proceed()

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        sel = FreeCADGui.Selection.getSelection()
        allSketches = True
        allDraft = True
        FreeCADGui.addModule("Draft")
        for obj in sel:
            if obj.isDerivedFrom("Sketcher::SketchObject"):
                allDraft = False
            elif obj.isDerivedFrom("Part::Part2DObjectPython"):
                allSketches = False
            else:
                allDraft = False
                allSketches = False
        if not sel:
            return
        elif allDraft:
            lines = ["Draft.makeSketch(FreeCADGui.Selection.getSelection(),autoconstraints=True)"]
            self.commit(translate("draft","Convert to Sketch"),
                        lines + ['FreeCAD.ActiveDocument.recompute()'])
        elif allSketches:
            lines = ["Draft.draftify(FreeCAD.ActiveDocument."+o.Name+",delete=False)" for o in sel]
            self.commit(translate("draft","Convert to Draft"),
                        lines + ['FreeCAD.ActiveDocument.recompute()'])
        else:
            lines = []
            for obj in sel:
                if obj.isDerivedFrom("Sketcher::SketchObject"):
                    lines.append("Draft.draftify(FreeCAD.ActiveDocument."+obj.Name+",delete=False)")
                elif obj.isDerivedFrom("Part::Part2DObjectPython"):
                    lines.append("Draft.makeSketch(FreeCAD.ActiveDocument."+obj.Name+",autoconstraints=True)")
                elif obj.isDerivedFrom("Part::Feature"):
                    #if (len(obj.Shape.Wires) == 1) or (len(obj.Shape.Edges) == 1):
                    lines.append("Draft.makeSketch(FreeCAD.ActiveDocument."+obj.Name+",autoconstraints=True)")
            self.commit(translate("draft","Convert"),
                        lines + ['FreeCAD.ActiveDocument.recompute()'])
        self.finish()


class Array(Modifier):
    """GuiCommand for the Draft_Array tool.

    Parameters
    ----------
    use_link: bool, optional
        It defaults to `False`. If it is `True`, the created object
        will be a `Link array`.
    """

    def __init__(self, use_link=False):
        Modifier.__init__(self)
        self.use_link = use_link

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Array',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Array", "Array"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Array", "Creates a polar or rectangular array from a selected object")}

    def Activated(self):
        Modifier.Activated(self)
        if not FreeCADGui.Selection.getSelection():
            if self.ui:
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Select an object to array")+"\n")
                self.call = self.view.addEventCallback("SoEvent",selectObject)
        else:
            self.proceed()

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        if FreeCADGui.Selection.getSelection():
            obj = FreeCADGui.Selection.getSelection()[0]
            FreeCADGui.addModule("Draft")
            self.commit(translate("draft","Array"),
                        ['obj = Draft.makeArray(FreeCAD.ActiveDocument.{},FreeCAD.Vector(1,0,0),FreeCAD.Vector(0,1,0),2,2,use_link={})'.format(obj.Name,self.use_link),
                         'Draft.autogroup(obj)',
                         'FreeCAD.ActiveDocument.recompute()'])
        self.finish()


class LinkArray(Array):
    """GuiCommand for the Draft_LinkArray tool."""

    def __init__(self):
        Array.__init__(self, use_link=True)

    def GetResources(self):
        return {'Pixmap'  : 'Draft_LinkArray',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_LinkArray", "LinkArray"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_LinkArray", "Creates a polar or rectangular link array from a selected object")}

class PathArray(Modifier):
    """The PathArray FreeCAD command definition"""

    def __init__(self,use_link=False):
        Modifier.__init__(self)
        self.use_link = use_link

    def GetResources(self):
        return {'Pixmap'  : 'Draft_PathArray',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_PathArray", "PathArray"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_PathArray", "Creates copies of a selected object along a selected path.")}

    def Activated(self):
        Modifier.Activated(self)
        if not FreeCADGui.Selection.getSelectionEx():
            if self.ui:
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Please select base and path objects")+"\n")
#                print("Please select base and path objects")
                self.call = self.view.addEventCallback("SoEvent",selectObject)
        else:
            self.proceed()

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        sel = FreeCADGui.Selection.getSelectionEx()
        if sel:
            base = sel[0].Object
            path = sel[1].Object
            pathsubs = list(sel[1].SubElementNames)
            defXlate = FreeCAD.Vector(0,0,0)
            defCount = 4
            defAlign = False
            FreeCAD.ActiveDocument.openTransaction("PathArray")
            Draft.makePathArray(base,path,defCount,defXlate,defAlign,pathsubs,use_link=self.use_link)
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()                                  # feature won't appear until recompute.
        self.finish()

class PathLinkArray(PathArray):
    "The PathLinkArray FreeCAD command definition"

    def __init__(self):
        PathArray.__init__(self,True)

    def GetResources(self):
        return {'Pixmap'  : 'Draft_PathLinkArray',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_PathLinkArray", "PathLinkArray"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_PathLinkArray", "Creates links of a selected object along a selected path.")}

class PointArray(Modifier):
    """The PointArray FreeCAD command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Draft_PointArray',
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_PointArray", "PointArray"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_PointArray", "Creates copies of a selected object on the position of points.")}

    def Activated(self):
        Modifier.Activated(self)
        if not FreeCADGui.Selection.getSelectionEx():
            if self.ui:
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Please select base and pointlist objects\n"))
                self.call = self.view.addEventCallback("SoEvent",selectObject)
        else:
            self.proceed()

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        sel = FreeCADGui.Selection.getSelectionEx()
        if sel:
            base  = sel[0].Object
            ptlst = sel[1].Object
            FreeCAD.ActiveDocument.openTransaction("PointArray")
            Draft.makePointArray(base, ptlst)
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()
        self.finish()


class Draft_Clone(Modifier):
    """The Draft Clone command definition"""

    def __init__(self):
        Modifier.__init__(self)
        self.moveAfterCloning = False

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Clone',
                'Accel' : "C,L",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Clone", "Clone"),
                'ToolTip' : QtCore.QT_TRANSLATE_NOOP("Draft_Clone", "Clones the selected object(s)")}

    def Activated(self):
        Modifier.Activated(self)
        if not FreeCADGui.Selection.getSelection():
            if self.ui:
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Select an object to clone")+"\n")
                self.call = self.view.addEventCallback("SoEvent",selectObject)
        else:
            self.proceed()

    def proceed(self):
        if self.call:
            self.view.removeEventCallback("SoEvent",self.call)
        if FreeCADGui.Selection.getSelection():
            l = len(FreeCADGui.Selection.getSelection())
            FreeCADGui.addModule("Draft")
            FreeCAD.ActiveDocument.openTransaction("Clone")
            nonRepeatList = []
            for obj in FreeCADGui.Selection.getSelection():
                if obj not in nonRepeatList:
                    FreeCADGui.doCommand("Draft.clone(FreeCAD.ActiveDocument.getObject(\""+obj.Name+"\"))")
                    nonRepeatList.append(obj)
            FreeCAD.ActiveDocument.commitTransaction()
            FreeCAD.ActiveDocument.recompute()
            FreeCADGui.Selection.clearSelection()
            for i in range(l):
                FreeCADGui.Selection.addSelection(FreeCAD.ActiveDocument.Objects[-(1+i)])
        self.finish()

    def finish(self,close=False):
        Modifier.finish(self,close=False)
        if self.moveAfterCloning:
            ToDo.delay(FreeCADGui.runCommand, "Draft_Move")


class Mirror(Modifier):
    """The Draft_Mirror FreeCAD command definition"""

    def GetResources(self):
        return {'Pixmap'  : 'Draft_Mirror',
                'Accel' : "M, I",
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Draft_Mirror", "Mirror"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Draft_Mirror", "Mirrors the selected objects along a line defined by two points")}

    def Activated(self):
        self.name = translate("draft","Mirror", utf8_decode=True)
        Modifier.Activated(self,self.name)
        self.ghost = None
        if self.ui:
            if not FreeCADGui.Selection.getSelection():
                self.ui.selectUi()
                FreeCAD.Console.PrintMessage(translate("draft", "Select an object to mirror")+"\n")
                self.call = self.view.addEventCallback("SoEvent",selectObject)
            else:
                self.proceed()

    def proceed(self):
        if self.call: self.view.removeEventCallback("SoEvent",self.call)
        self.sel = FreeCADGui.Selection.getSelection()
        self.ui.pointUi(self.name)
        self.ui.modUi()
        self.ui.xValue.setFocus()
        self.ui.xValue.selectAll()
        # self.ghost = trackers.ghostTracker(self.sel) TODO: solve this (see below)
        self.call = self.view.addEventCallback("SoEvent",self.action)
        FreeCAD.Console.PrintMessage(translate("draft", "Pick start point of mirror line")+"\n")
        self.ui.isCopy.hide()

    def finish(self,closed=False,cont=False):
        if self.ghost:
            self.ghost.finalize()
        Modifier.finish(self)
        if cont and self.ui:
            if self.ui.continueMode:
                FreeCADGui.Selection.clearSelection()
                self.Activated()

    def mirror(self,p1,p2,copy=False):
        """mirroring the real shapes"""
        sel = '['
        for o in self.sel:
            if len(sel) > 1:
                sel += ','
            sel += 'FreeCAD.ActiveDocument.'+o.Name
        sel += ']'
        FreeCADGui.addModule("Draft")
        self.commit(translate("draft","Mirror"),
                    ['Draft.mirror('+sel+','+DraftVecUtils.toString(p1)+','+DraftVecUtils.toString(p2)+')',
                     'FreeCAD.ActiveDocument.recompute()'])

    def action(self,arg):
        """scene event handler"""
        if arg["Type"] == "SoKeyboardEvent":
            if arg["Key"] == "ESCAPE":
                self.finish()
        elif arg["Type"] == "SoLocation2Event": #mouse movement detection
            self.point,ctrlPoint,info = getPoint(self,arg)
            if (len(self.node) > 0):
                last = self.node[-1]
                if self.ghost:
                    if self.point != last:
                        # TODO : the following doesn't work at the moment
                        mu = self.point.sub(last).normalize()
                        if FreeCAD.GuiUp:
                            mv = FreeCADGui.ActiveDocument.ActiveView.getViewDirection().negative()
                        else:
                            mv = FreeCAD.Vector(0,0,1)
                        mw = mv.cross(mu)
                        import WorkingPlane
                        tm = WorkingPlane.plane(u=mu,v=mv,w=mw,pos=last).getPlacement().toMatrix()
                        m = self.ghost.getMatrix()
                        m = m.multiply(tm.inverse())
                        m.scale(FreeCAD.Vector(1,1,-1))
                        m = m.multiply(tm)
                        m.scale(FreeCAD.Vector(-1,1,1))
                        self.ghost.setMatrix(m)
            if self.extendedCopy:
                if not hasMod(arg,MODALT): self.finish()
            redraw3DView()
        elif arg["Type"] == "SoMouseButtonEvent":
            if (arg["State"] == "DOWN") and (arg["Button"] == "BUTTON1"):
                if self.point:
                    self.ui.redraw()
                    if (self.node == []):
                        self.node.append(self.point)
                        self.ui.isRelative.show()
                        if self.ghost:
                            self.ghost.on()
                        FreeCAD.Console.PrintMessage(translate("draft", "Pick end point of mirror line")+"\n")
                        if self.planetrack:
                            self.planetrack.set(self.point)
                    else:
                        last = self.node[0]
                        if self.ui.isCopy.isChecked() or hasMod(arg,MODALT):
                            self.mirror(last,self.point,True)
                        else:
                            self.mirror(last,self.point)
                        if hasMod(arg,MODALT):
                            self.extendedCopy = True
                        else:
                            self.finish(cont=True)

    def numericInput(self,numx,numy,numz):
        """this function gets called by the toolbar when valid x, y, and z have been entered there"""
        self.point = Vector(numx,numy,numz)
        if not self.node:
            self.node.append(self.point)
            if self.ghost:
                self.ghost.on()
            FreeCAD.Console.PrintMessage(translate("draft", "Pick end point of mirror line")+"\n")
        else:
            last = self.node[-1]
            if self.ui.isCopy.isChecked():
                self.mirror(last,self.point,True)
            else:
                self.mirror(last,self.point)
            self.finish()


# ---------------------------------------------------------------------------
# Snap tools
# ---------------------------------------------------------------------------
from draftguitools.gui_snaps import Draft_Snap_Lock
from draftguitools.gui_snaps import Draft_Snap_Midpoint
from draftguitools.gui_snaps import Draft_Snap_Perpendicular
from draftguitools.gui_snaps import Draft_Snap_Grid
from draftguitools.gui_snaps import Draft_Snap_Intersection
from draftguitools.gui_snaps import Draft_Snap_Parallel
from draftguitools.gui_snaps import Draft_Snap_Endpoint
from draftguitools.gui_snaps import Draft_Snap_Angle
from draftguitools.gui_snaps import Draft_Snap_Center
from draftguitools.gui_snaps import Draft_Snap_Extension
from draftguitools.gui_snaps import Draft_Snap_Near
from draftguitools.gui_snaps import Draft_Snap_Ortho
from draftguitools.gui_snaps import Draft_Snap_Special
from draftguitools.gui_snaps import Draft_Snap_Dimensions
from draftguitools.gui_snaps import Draft_Snap_WorkingPlane
from draftguitools.gui_snaps import ShowSnapBar

# ---------------------------------------------------------------------------
# Adds the icons & commands to the FreeCAD command manager, and sets defaults
# ---------------------------------------------------------------------------

# drawing commands

# modification commands
FreeCADGui.addCommand('Draft_Move',Move())
FreeCADGui.addCommand('Draft_Rotate',Rotate())
FreeCADGui.addCommand('Draft_Offset',Offset())
FreeCADGui.addCommand('Draft_Join',Join())
FreeCADGui.addCommand('Draft_Split',Split())
FreeCADGui.addCommand('Draft_Upgrade',Upgrade())
FreeCADGui.addCommand('Draft_Downgrade',Downgrade())
FreeCADGui.addCommand('Draft_Trimex',Trimex())
FreeCADGui.addCommand('Draft_Scale',Scale())
FreeCADGui.addCommand('Draft_Drawing',Drawing())
FreeCADGui.addCommand('Draft_SubelementHighlight', SubelementHighlight())
FreeCADGui.addCommand('Draft_WireToBSpline',WireToBSpline())
FreeCADGui.addCommand('Draft_Draft2Sketch',Draft2Sketch())
FreeCADGui.addCommand('Draft_Array',Array())
FreeCADGui.addCommand('Draft_LinkArray',LinkArray())
FreeCADGui.addCommand('Draft_Clone',Draft_Clone())
FreeCADGui.addCommand('Draft_PathArray',PathArray())
FreeCADGui.addCommand('Draft_PathLinkArray',PathLinkArray())
FreeCADGui.addCommand('Draft_PointArray',PointArray())
FreeCADGui.addCommand('Draft_Mirror',Mirror())
FreeCADGui.addCommand('Draft_Stretch',Stretch())

# context commands
FreeCADGui.addCommand('Draft_ApplyStyle',ApplyStyle())
FreeCADGui.addCommand('Draft_Shape2DView',Shape2DView())

# a global place to look for active draft Command
FreeCAD.activeDraftCommand = None
