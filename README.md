# Blender Ragdoll

Blender Ragdoll extends Blender's Armature Objects with Rigid Body Simulation properties. Using Blender's native objects and object relations, the system creates serveral layers of meshes and empty objects and offers an interface to control an armature's animation and simulation properties. An armature's transformation can be blended between animation and simulation or a combination of both. 

## Quickstart
+ <b>Install Ragdoll:</b> Download ZIP file from packages directory. In <i>Blender Preferences / Add-ons</i> click <i>Install</i> and select ZIP file. Make sure the addon is enabled, you can filter by <i>Animation</i> to find the addon in the list.  

+ <b>Obtain Rigged Mesh:</b> Not everybody has a mesh with an armature at hand. Some websites, for example Mixamo, offer rigged FBX files to download for free. These can be imported to blender. You could also use the example file supplied. TODO: supply file. 

+ <b>Rigid Body World:</b> With an armature object selected, a Ragdoll Panel is shown in the <i>Physics</i> tab of the Property Panel. If your scene does not have a <i>Rigid Body World</i> or <i>Rigid Body Constraints</i> set, you will be prompted to add both.

+ <b>Add Ragdoll to Armature:</b> Now your simulation environment is set up, you can create a Ragdoll based on the selected armature by clicking <i>Create</i> in the Ragdoll Panel. The operator works in both Pose Mode and Object Mode. In Pose Mode it will add Ragdoll functionality to all selected bones, while in Object Mode all visible bones will be used. If your armature containts leaf bones on its chain ends, make sure to hide/delete/not select those unless you wish to simulate them. Also, you might want to hide complex parts such as fingers. 

+ <b>Extend Ragdoll:</b> It is possible to build your Ragdoll step by step. It's recommended to use on selected bones in Pose Mode but works in Object Mode, too.

+ <b>Play your Animation:</b> A basic simulation has been set up and you should see your armature and/or charactor fall down when you hit <i>Play Animation</i>, unless you have other rigid bodies in your scene, for example a floor. You can add a floor by using <i>Add Menu >  Mesh > Plane</i> in the viewport. You can add a Rigid Body component to the plane by using <i>Object Menu > Rigid Body > Add Passive</i>.

+ <b>Precision and Cache:</b> Depending on the complexity of your setup, you might want to allow for a more sophisticated simulation by calculating more Simulation Substeps and / or Constraint Solver Iterations. The settings of your scene's Rigid Body World can be found in the <i>Scene Properties Tab</i> inside the Rigid Body World Panel. Here you can also set the frame range of your simulation. Occasionally, simulations don't seem to update and it can help to delete the cache by using <i>Delete All Bakes</i>.

## Quickstart, extended

+ <b>Fine Tune Constraints:</b> The Constraints Panel offers controls to define distance and rotational limits to the joints of your rig, as well as their display size. Limits can be defined by either using default values or a preset. A preset for an armature downloaded from Mixamo is supplied, as well as version with somewhat blenderized naming conventions. TODO: Blenderized version.

+ <b>Fine Tune Geometry:</b> In the Geometry Panel you can modify the relative scale of the geometry created. If you choose <i>Solid</i> Viewport Display you can see your Ragdoll in all it's glory.  

+ <b>Mesh Approximation:</b> If your armature has a mesh to deform, you can use this mesh to approximate the shape of your Ragdoll. If a mesh is selected as <i>Deform Mesh</i>, you can use <i>Approximate</i> to snap the Ragdoll's cubes' faces to this mesh. <b>Note</b>: This operator might take some time, depending on your setup's complexity and resources. It is recommended to be used in Pose Mode on selected bones.  

+ <b>Reset Approximation:</b> Approximation of selected bones' meshes can be reset using the reset button. Approximated meshes are exempt from being scaled using <i>Relative Scale</i> or <i>Width Limits</i> which can be reset.
  
+ <b>Toggle Animation:</b> In the <i>Animated</i> Panel, you can toggle, keyframe and blend the influence of animation and simulation.

+ <b>Wiggle:</b>
Using wiggles allows you to simulate on top of an animation. Wiggles are a set of objects tied to the armature's animated bones. Wiggle constraints define, How much the Ragdoll's simulated bones may deviated from the animated bones. Use low values to add weight and character to your otherwise generic motion capture data. Or use higher values to achieve sillyness. 
+ <b>Hooks:</b> 
Hooks allow you to pin a bone's physical representation to another object, which is represented by an additional bone. Hooking multiple bones to one object is possible, even though it is an experimental feature. Hooks can be added in Pose Mode. Select the bone you wish to took and click <i>Add Hook</i>. Hook objects expose the properties of the rigid body constraint that is assigned to them and can be set up individually.
+ <b>Naming:</b> As a Ragdoll consists of many objects, names become relevant. In the Naming Panel you can change the suffixes of your Ragdoll objects.
<i>Replace</i> lets the user change the names of a Ragdoll Armature's bones and all related objects. Fields are <i>source, target, suffix-if-source</i>. The suffix allows to modify naming conventions for left/right. For example, with source="Left", target="" and suffix=".L" a bone named "LeftHand" will be renamed to "Hand.L", which is conformal with Blender's naming convention for bones.

## Ragdoll Objects

+ <b>Deform Rig:</b> 
The Armature selected upon Ragdoll creation is used to deform meshes and will not be modified by the setup except for pose constraints that transfer transformations from either the control rig or the simulation.

+ <b>Control Rig:</b>
A duplicate os the original armature to pose and animate both simulation elements and deform rig.

+ <b>Rigid Bodies </b> are mesh objects used by the simulation as physical representations of bones. A Ragdolls rigid body objects are organized in a collection and are children of a control rig's pose bones. related objects are: 
    + <b>Rigid Body Constraints </b> define the joints between bones and are parented to the deform rig. These constraints are children of their corresponding pose bones within the control rig.

    + <b>Rigid Body Connectors</b> are children of rigid body objects and follow their transforms. As rigid body simulation uses objects' pivot points as centers of mass, this additional layer of objects is needed. Connectors are located at the bones' origin and function as transform targets for the deform rig. 
    

+ <b>Wiggles</b>
Wiggles represent an additional layer of rigid body objects allowing to simulate on top of animation. While the meshes are not part of any collision group, they are still required as constraints can only bind mesh type objects with rigid bodies set up.
    + <b>Wiggle Constraints</b> bind primary rigid body objects to wiggle objects.

+ <b>Hooks:</b>
Hooks can be added to fix the simulation rig to an additional bone. While the meshes are not part of any collision group, they are still required as constraints can only bind mesh type objects with rigid bodies set up.
    + <b>Hook Constraints</b> bind primary rigid body objects to hook objects.


## Ragdoll Panel
The main Panel let's you add a Ragdoll setup to the selected armature object. If a setup for this object already exists, it can be extended by selected or newly visible pose bones instead.

If a <i>Deform Rig</i> is selected the user can either delete the Ragdoll or select the <i>Control rig</i>. Other options will be disabled.

## Constraints

![enter image description here](https://raw.githubusercontent.com/schnollie/blender_Ragdoll/main/images/constraints.jpeg)

### Preset
To control angular and linear limits of constraints more precisely, presets can be created and modified in blender's text editor or externally. A simple preset for a rig from Mixamo is supplied. 


 The JSON File lists bone names and some options in a dictionary. Bone names can contain undesired elements, such as branding. If bone names need to be retained, The parameter "strip" can be used to avoid repetition of it's value when working with the preset file.  If bones can be renamed, see <i>Naming</i> below. 
A label next to the file selection indicates if your preset has been modified and/or saved to disk. Per default, the text will be saved with the scene as well. There are three buttons, <i>load preset</i>,  <i>new preset</i> and <i>apply preset</i>,  next to the preset  selection. 

### Default Values
If no preset is supplied or the a bone is not found within a preset, default values for the bone's rigid constraints are set. Distance defines, how far a bone can move from it's parent along all axis,  Angle defines the maximum rotation a bone can rotated from it's parent's orientation along all axis. 

### Display Size
Constraint Objects are set up to be displayed in a scale relative to their rigid body objects. <i>Factor</i> is multiplied with the object's display size, <i>Offset</i> is added. 


## Geometry

![enter image description here](https://raw.githubusercontent.com/schnollie/blender_Ragdoll/main/images/geometry.jpeg)

### Relative Scale
Dimensions of rigid body geometry, relative to the bones' lengths.

###  Width Limits
Minimum and maximum dimensions for rigid body meshes.
### Display As
Viewport display of primary rigid body objects.

### Mesh Approximation
Mesh approximation allows you to approximate rigid body geometry of selected pose bones. 
### Deform Mesh
Deform mesh is the target of the approximation. The cubes' faces  centers are projected to the targets surface along their local X and Z axis. 
### Offset
Offset distance added to projection. 
### Projection Threshold
Maximum distance the appromiation uses to find and intersection.
### Rigid Bodies Approximate
Starts approximation. Depending on the setup's complexity resources the process can take up to a few minutes.
An approximated rigid body object is protected from being modified by relative scale and/or scale limits. Protection can be unset by either selecting pose bones and using <i>Rigid Bodies Reset</i> or by selecting the Mesh object and unsetting <i>Protect Aprroximate</i> in the object's Properties Panel in <i>Physics > Ragdoll</i>  
#### Rigid Bodies Reset
Resets the selected bones' meshes to relative dimensions defined above.

## Animated
If checked, deform rig will follow control rig's animation, otherwise it will follow the Rigid Body Simulation. 
![enter image description here](https://raw.githubusercontent.com/schnollie/blender_Ragdoll/main/images/animated.jpeg)
### Override
Fades between transforms of Control Rig's animation and rigid body simulation.
## Wiggle
![enter image description here](https://raw.githubusercontent.com/schnollie/blender_Ragdoll/main/images/wiggle.jpeg)
### Display As
TODO
### Scale
TODO
### Limit Linear
TODO
### Limit Angular
TODO
### Springs
TODO
#### Stiffness
TODO
#### Damping
TODO
#### Add/Remove Drivers
TODO 

### Falloff
TODO
#### Type
TODO
#### Factor
TODO
#### Invert
TODO
#### Ends
TODO

## Hooks
![enter image description here](https://raw.githubusercontent.com/schnollie/blender_Ragdoll/main/images/hooks.jpeg)
Hooks are listed by the name of the bone they are hooked to.

### Enable Hook
Using the checkbox next to the hooks name users can enable and disable hooks. 
### Remove Hook
Hooks can be removed by clicking the <i>X</i> in the top right corner of their box.
### Hook Constraint Properties
TODO
#### Constraint Objects
TODO
#### Linear Constraint Limits
TODO
#### Angular Constraint Limits
TODO

## Naming
![enter image description here](https://raw.githubusercontent.com/schnollie/blender_Ragdoll/main/images/naming.jpeg)
### Suffixes
TODO
### Replace
TODO
## Collections
![enter image description here](https://raw.githubusercontent.com/schnollie/blender_Ragdoll/main/images/collections.jpeg)
The collection tab displays collections used for this Ragdoll. Read-only.





















