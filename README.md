# Blender RagDoll

Blender RagDoll extends Blender's Armature Objects with Rigid Body Simulation properties.   

+ <b>Deform Rig:</b> 
The Armature selected upon ragdoll creation is used to deform meshes and will not be modified by the setup except for pose constraints that transfer transformations from either the control rig or the simulation.

+ <b>Control Rig:</b>
A duplicate os the original armature to pose and animate both simulation elements and deform rig.

+ <b>Rigid Bodies </b> are mesh objects used by the simulation as physical representations of bones. A ragdolls rigid body objects are organized in a collection and are children of a control rig's pose bones. related objects are: 
    + <b>Rigid Body Constraints </b> define the joints between bones and are parented to the deform rig. These constraints are children of their corresponding pose bones within the control rig.

    + <b>Rigid Body Connectors</b> are children of rigid body objects and follow their transforms. As rigid body simulation uses objects' pivot points as centers of mass, this additional layer of objects is needed. Connectors are located at the bones' origin and function as transform targets for the deform rig. 
    

+ <b>Wiggles</b>
Wiggles represent an additional layer of rigid body objects allowing to simulate on top of animation. While the meshes are not part of any collision group, they are still required as constraints can only bind mesh type objects with rigid bodies set up.
    + <b>Wiggle Constraints</b> bind primary rigid body objects to wiggle objects.

+ <b>Hooks:</b>
Hooks can be added to fix the simulation rig to an additional bone. While the meshes are not part of any collision group, they are still required as constraints can only bind mesh type objects with rigid bodies set up.
    + <b>Hook Constraints</b> bind primary rigid body objects to hook objects.


## RagDoll Panel
The main panel let's you add a ragdoll setup to the selected armature object. If a setup for this object already exists, it can be extended by selected or newly visible pose bones instead.

If a <i>Deform Rig</i> is selected the user can either delete the ragdoll or select the <i>Control rig</i>. Other options will be disabled.

## Constraints

![enter image description here](https://raw.githubusercontent.com/schnollie/blender_ragdoll/main/images/constraints.jpeg)

### Preset
To control angular and linear limits of constraints more precisely, presets can be created and modified in blender's text editor or externally. A simple preset for a rig from Mixamo is supplied. 


 The JSON File lists bone names and some options in a dictionary. Bone names can contain undesired elements, such as branding. If bone names need to be retained, The parameter "strip" can be used to avoid repetition of it's value when working with the preset file.  If bones can be renamed, see <i>Naming</i> below. 
A label next to the file selection indicates if your preset has been modified and/or saved to disk. Per default, the text will be saved with the scene as well. There are three buttons, <i>load preset</i>,  <i>new preset</i> and <i>apply preset</i>,  next to the preset  selection. 

### Default Values
If no preset is supplied or the a bone is not found within a preset, default values for the bone's rigid constraints are set. Distance defines, how far a bone can move from it's parent along all axis,  Angle defines the maximum rotation a bone can rotated from it's parent's orientation along all axis. 

### Display Size
Constraint Objects are set up to be displayed in a scale relative to their rigid body objects. <i>Factor</i> is multiplied with the object's display size, <i>Offset</i> is added. 


## Geometry

![enter image description here](https://raw.githubusercontent.com/schnollie/blender_ragdoll/main/images/geometry.jpeg)

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
An approximated rigid body object is protected from being modified by relative scale and/or scale limits. Protection can be unset by either selecting pose bones and using <i>Rigid Bodies Reset</i> or by selecting the Mesh object and unsetting <i>Protect Aprroximate</i> in the object's Properties panel in <i>Physics > RagDoll</i>  
#### Rigid Bodies Reset
Resets the selected bones' meshes to relative dimensions defined above.

## Animated
If checked, deform rig will follow control rig's animation, otherwise it will follow the Rigid Body Simulation. 
![enter image description here](https://raw.githubusercontent.com/schnollie/blender_ragdoll/main/images/animated.jpeg)
### Override
Fades between transforms of Control Rig's animation and rigid body simulation.
## Wiggle
![enter image description here](https://raw.githubusercontent.com/schnollie/blender_ragdoll/main/images/wiggle.jpeg)
### Display As
### Scale

### Limit Linear

### Limit Angular

### Springs
#### Stiffness
#### Damping
#### Add/Remove Drivers 

### Falloff
#### Type
#### Factor
#### Invert
#### Ends

## Hooks
![enter image description here](https://raw.githubusercontent.com/schnollie/blender_ragdoll/main/images/hooks.jpeg)
Hooks are listed by the name of the bone they are hooked to.

### Enable Hook
Using the checkbox next to the hooks name users can enable and disable hooks. 
### Remove Hook
Hooks can be removed by clicking the <i>X</i> in the top right corner of their box.
### Hook Constraint Properties
#### Constraint Objects
#### Linear Constraint Limits
#### Angular Constraint Limits

## Naming
![enter image description here](https://raw.githubusercontent.com/schnollie/blender_ragdoll/main/images/naming.jpeg)
### Suffixes

### Replace

## Collections
![enter image description here](https://raw.githubusercontent.com/schnollie/blender_ragdoll/main/images/collections.jpeg)
The collection tab displays collections used for this ragdoll. Read-only.





















