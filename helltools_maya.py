'''
HellTools
-----
ADDED

    

---
WIP
    

-----
TO-DO
    


=====
Index
    01 : GPU Cache
    02 : Locators
    03 : Hierarchy

======
PYTHON

import tlp_animBuilder
reload(tlp_animBuilder)
from tlp_animBuilder import animBuildUI_window

animBuildUI_window()

'''
import maya.mel as mel
import maya.cmds as cmds
from maya.cmds import file
from maya.mel import eval
from pymel.core.system import getFileList
from pymel.core.general import ls, select, delete, spaceLocator, objExists, createNode, setAttr, group
from pymel.core.animation import parentConstraint
from pymel.core.windows import window, deleteUI, button, verticalLayout, separator, showWindow
from pymel.core import Callback
import os
import apero.aperoWrapper as wrap


## hell tools externals 

import twinSave as ts


############# Version #############


ver = '1.1.3'


###################################


#                        #
# path & folder handling #
#                        #

def animBuild_getScenePath():
  
    scenePath  =  file( q = 1, sn = 1 )
    
    return scenePath


def animBuild_getShotSlug( scenePath ):
  
    slug  =  scenePath . split( '/' ) . pop() . split( '_' ) [2]
    
    return slug


def animBuild_getTypeFromSlug( slug ):
    
    if 'sh' in slug:
        sceneType = 'sh'
    elif 'sc' in slug:
        sceneType = 'sc'
    
    return sceneType

def animBuild_getCachePrefix( slug ):
    
    typ     =  animBuild_getTypeFromSlug( slug )
    prefix  =  'tlp_' + typ + '_' + slug + '_gpc'
    
    return prefix


def animBuild_getWorkDir( scenePath ):
    
    currentPathToken  =  scenePath . split( '/' )
    currentScene      =  currentPathToken  .  pop()
    workDir           =  '/' .join( currentPathToken ) + '/'
    
    return workDir


def animBuild_getPublishDir( slug ):
    
    typ             =  animBuild_getTypeFromSlug( slug )
    publishPath     =  '/systeme/apero/prod/tlp/' + typ + '/' + slug + '/gpc/'
    publishDirList  =  [ subdir for subdir in os.listdir( publishPath ) if os.path.isdir( publishPath + subdir ) ]
    publishDir      =  publishPath + publishDirList . pop() + '/'
    
    return publishDir


def animBuild_getLocalCacheDir( scenePath ):
    
    currentSceneSlug    =  animBuild_getShotSlug( scenePath )
    currentWorkDir      =  animBuild_getWorkDir( scenePath )
    hintCacheDir        =  animBuild_getCachePrefix( currentSceneSlug )
    currentWorkDirList  =  [ subdir for subdir in os.listdir( currentWorkDir ) if os.path.isdir( currentWorkDir + subdir ) and hintCacheDir in subdir ]
    localCacheDirName   =  hintCacheDir + '.1.gpuCache'
    
    if not currentWorkDirList == []:
        localCacheDir   =  currentWorkDir + currentWorkDirList . pop()
    else:
        localCacheDir   =  currentWorkDir + localCacheDirName
        os . mkdir( localCacheDir )
    
    localCacheDir  +=  '/'
    return localCacheDir

#                    #
# gpu cache handling #
#                    #

def animBuild_createLocalCache():    							###  ADD WARNING IF FOLDER NOT EMPTY ?
    
    scenePath         =  animBuild_getScenePath()
    cacheDir          =  animBuild_getLocalCacheDir( scenePath )
    
    currentSceneSlug  =  animBuild_getShotSlug( scenePath )
    filePrefix        =  animBuild_getCachePrefix( currentSceneSlug ) + '__'

    if not ls( sl = 1 ) == []:
        eval( 'string $nodes[] = ` getGpuCacheExportNodeList `' )
        eval( 'gpuCache -startTime ` playbackOptions -q -min ` -endTime ` playbackOptions -q -max ` -simulationRate 1 -sampleMultiplier 1 -optimize -optimizationThreshold 40000 -directory \"' + cacheDir + '\" -filePrefix \"' + filePrefix + '\" $nodes' )


def animBuild_importCache( path ):
    
    cacheFileList  =  getFileList( folder = path )
    
    for cacheFile in cacheFileList:
        
        cacheFilePath  =  path + cacheFile
    
        cacheToken  =  cacheFile.split( '.' )
        cacheToken  . pop()
        fileName    = '_' . join( cacheToken )
        nodeName    = eval( '$nodeName = `formValidObjectName( \"' + fileName + '\" )`' )
        
        xformNode  =  createNode( 'transform', name= nodeName )
        cacheNode  =  createNode( 'gpuCache', name = nodeName + 'Shape', parent = xformNode )
        setAttr( cacheNode + '.cacheFileName', cacheFilePath, type = 'string' )


def animBuild_publishLocalCache():
    
    scenePath  =  animBuild_getScenePath()
    cacheDir   =  animBuild_getLocalCacheDir( scenePath )
    sceneSlug  =  animBuild_getShotSlug( scenePath )
    
    # remove '/' at the end
    cacheDirPublishPath  =  cacheDir[ 0 : -1 ]
    
    # PUBLISH
    out, err, cmd  =  wrap.Publish( cacheDirPublishPath, sceneSlug + ' gpu cache from layout' )
    print(err)


#                               #
#  from tlp_locatorOnTarget.py  #
#                               #

def animBuild_locatorOnTarget(levels=0, start=0, suf='loc', match=[]):
    locs = []
    for sl in ls(sl=1):
        split = sl.split(':')
        i = len(split)
        if levels > i or levels == 0: levels = i
        name = '___'.join(split[start:levels])+'___'+suf
        
        for old, new in match:
            if old in name:
                print ('name match: '+name+'\n')
                name = name.replace(old, new)
        
        loc = spaceLocator(n=name)
        delete(parentConstraint(sl, loc))
        locs.append(loc)
    select(locs)


def animBuild_retrieveFromLocators(levels=0, start=0):
    notFounds = []
    targets = []
    
    for loc in ls(sl=1):
        split = loc.split('___')
        i = len(split)-1
        if levels > i or levels == 0: levels = i
        target = ':'.join(split[start:levels])
        
        if objExists(target):
            delete(parentConstraint(loc, target))
            targets.append(target)
        else:
            notFounds.append(target)
    
    if len(notFounds):
        print ('Some objects were not found in the scene :')
        for obj in notFounds: print( '\t\t'+obj)
    
    select(targets)
#                  #
#  comet rename    #
#                  #    

def helltools_cometRename():
    
    mel.eval('cometRename')    
    
#                          #
#  NightShade UV editor    #
#                          #    

def helltools_nightShadeUV():
    
    mel.eval('NightshadeUVEditor')    
  


    
#                          #
#  create SSU hierarchy    #
#                          #

def animBuild_createSsuHierarchy():
    
    master  =  group( n = 'grp_master', em = 1 )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # camera
    m_cam       =  group( n = 'grp_camera', em = 1, p = master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    m_cam_lock  =  group( n = 'grp_camera_hide_reference', em = 1, p = m_cam )
    setAttr( m_cam_lock + '.inheritsTransform', 0 )
    setAttr( m_cam_lock + '.overrideEnabled', 1 )
    setAttr( m_cam_lock + '.overrideDisplayType', 2 )					### & hide ?
    
    # characters
    m_chars  =  group( n = 'grp_characters', em = 1, p = master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # props
    m_props       =  group( n = 'grp_props', em = 1, p = master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    m_props_anim  =  group( n = 'grp_props_animated', em = 1, p = m_props )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    m_props_stat  =  group( n = 'grp_props_static', em = 1, p = m_props )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # gpu_cache
    m_lay           =  group( n = 'grp_layout', em = 1, p = master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 0;' )
    m_lay_gpu       =  group( n = 'grp_gpu_cache', em = 1, p = m_lay )
    eval( 'guerillaCreateSetBool "GuerillaExport" 0;' )
    m_lay_gpu_lock  =  group( n = 'grp_gpu_cache_transformLocked_reference', em = 1, p = m_lay_gpu )
    eval( 'guerillaCreateSetBool "GuerillaExport" 0;' )
    m_lay_gpu_anim  =  group( n = 'grp_gpu_cache_animated', em = 1, p = m_lay_gpu_lock )
    eval( 'guerillaCreateSetBool "GuerillaExport" 0;' )
    m_lay_gpu_stat  =  group( n = 'grp_gpu_cache_static', em = 1, p = m_lay_gpu_lock )
    eval( 'guerillaCreateSetBool "GuerillaExport" 0;' )
    setAttr( m_lay_gpu_lock + '.inheritsTransform', 0 )
    setAttr( m_lay_gpu_lock + '.overrideEnabled', 1 )
    setAttr( m_lay_gpu_lock + '.overrideDisplayType', 2 )
    
    # garbage
    m_garb  =  group( n = 'grp_garbage_not_for_guerilla', em = 1, p = master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 0;' )
    
    select( cl = 1 )
  
 
    
#                        #
#  make STD hierarchy    #
#                        #

def animBuild_createStdHierarchy ():
    
    # grp master 
    master  =  group( n = 'grp_master', em = 1 )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp ass
    ass_grp  =  group( n = 'ass_grp', em = 1, p = master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )

   # grp anf
    m_chars  =  group( n = 'grp_anf', em = 1, p = ass_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp flo
    m_props       =  group( n = 'grp_flo', em = 1, p = ass_grp)
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp add
    m_props       =  group( n = 'grp_add', em = 1, p = ass_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp garbage
    m_garb  =  group( n = 'grp_garbage_not_for_guerilla', em = 1, p = ass_grp)
    eval( 'guerillaCreateSetBool "GuerillaExport" 0;' )
    
    # grp std
    m_props       =  group( n = 'for_std', em = 1, p = master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp add
    m_props       =  group( n = 'grp_add', em = 1, p = master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp garbage
    m_garb  =  group( n = 'grp_garbage_not_for_guerilla', em = 1, p = master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 0;' )
    
    select( cl = 1 )


#                             #
#  make  new STD hierarchy    #
#                            #

def Helltools_newSTDHierarchy ():
    
    # grp master 
    master  =  group( n = 'grp_std', em = 1 )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )

    # grp cam 
    master  =  group( n = 'grp_cam', em = 1 )
    eval( 'guerillaCreateSetBool "GuerillaExport" 0;' )

#                             #
#  make  new ssu hierarchy    #
#                             #

def Helltools_newSSUHierarchy ():
    

    
    master  =  group( n = 'grp_master', em = 1 )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # garbage
    m_garb  =  group( n = 'grp_garbage_not_for_guerilla', em = 1, p = master)
    eval( 'guerillaCreateSetBool "GuerillaExport" 0;' )
   
    
    
    # core groups
    #animated
    m_anim  =  group( n = 'animated', em = 1, p = master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # characters
    m_chars  =  group( n = 'grp_characters', em = 1, p = m_anim)
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
   
    # props
    m_props  =  group( n = 'grp_props', em = 1, p = m_anim)
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # sets
    m_set  =  group( n = 'grp_sets', em = 1, p = m_anim)
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )




    #static
    m_stat  =  group( n = 'static', em = 1, p = master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 0;' )
    
    





    

#                                     #
#  make standard modeling hierarchy   #
#                                     #

def Helltools_createCharacterHierarchy ():
    
    # grp master 
    all  =  group( n = 'all', em = 1 )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp trs_master
    trs_master =  group( n = 'trs_master', em = 1, p = all )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp trs_shot
    trs_shot =  group( n = 'trs_shot', em = 1, p = trs_master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp trs_aux
    trs_aux =  group( n = 'trs_aux', em = 1, p = trs_shot )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp model
    model_grp =  group( n = 'model', em = 1, p = trs_aux )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # reder grp 
    render_grp =  group( n = 'render_grp', em = 1, p = model_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp bodyPrimary_grp 
    bodyPrimary_grp =  group( n = 'bodyPrimary_grp', em = 1, p = render_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp facePrimary_grp 
    facePrimary_grp =  group( n = 'facePrimary_grp', em = 1, p = render_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp hair_grp 
    hair_grp =  group( n = 'hair_grp', em = 1, p = render_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp bodyMisc_grp 
    bodyMisc_grp  =  group( n = 'bodyMisc_grp', em = 1, p = render_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp cloth_grp 
    cloth_grp  =  group( n = 'cloth_grp', em = 1, p = render_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp hairGuide_grp 
    hairGuide_grp =  group( n = 'hairGuide_grp', em = 1, p = render_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )

    # grp characterGuide_grp 
    characterGuide_grp =  group( n = 'characterGuide_grp', em = 1, p = render_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
        
    # grp intermediate_grp 
    intermediate_grp  =  group( n = 'intermediate_grp', em = 1, p = model_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )    
    
    # grp faceIntermediate_grp 
    render_grp =  group( n = 'faceIntermediate_grp', em = 1, p = intermediate_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
       
    # grp clothIntermediate_grp 
    render_grp =  group( n = 'clothIntermediate_grp', em = 1, p = intermediate_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' ) 

#                                     #
#  make standard modeling hierarchy   #
#                                     #

def Helltools_createPropsHierarchy ():
    
    # grp master 
    all  =  group( n = 'all', em = 1 )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp trs_master
    trs_master =  group( n = 'trs_master', em = 1, p = all )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp trs_shot
    trs_shot =  group( n = 'trs_shot', em = 1, p = trs_master )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp trs_aux
    trs_aux =  group( n = 'trs_aux', em = 1, p = trs_shot )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp model
    model_grp =  group( n = 'model', em = 1, p = trs_aux )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # render grp 
    render_grp =  group( n = 'render_grp', em = 1, p = model_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp box_grp 
    box_grp =  group( n = 'box_grp', em = 1, p = render_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
    # grp props_grp 
    props_grp =  group( n = 'props_grp', em = 1, p = render_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
    
        
    # grp intermediate_grp 
    intermediate_grp  =  group( n = 'intermediate_grp', em = 1, p = model_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )    
    
    # grp faceIntermediate_grp 
    render_grp =  group( n = 'faceIntermediate_grp', em = 1, p = intermediate_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' )
       
    # grp clothIntermediate_grp 
    render_grp =  group( n = 'clothIntermediate_grp', em = 1, p = intermediate_grp )
    eval( 'guerillaCreateSetBool "GuerillaExport" 1;' ) 



#                           #
#  scene resolution   #
#                           #

def Helltools_set2KRender ():	
	
	setAttr ("defaultResolution.width", 2048)
	setAttr ("defaultResolution.height", 858)
	setAttr ("defaultResolution.pixelAspect", 1)
	setAttr ("defaultResolution.lockDeviceAspectRatio", 1)
	setAttr ("defaultResolution.deviceAspectRatio", 2.387)

def Helltools_set1080Render ():	
	
	setAttr ("defaultResolution.width", 1920)
	setAttr ("defaultResolution.height", 1080)
	setAttr ("defaultResolution.pixelAspect", 1)
	setAttr ("defaultResolution.lockDeviceAspectRatio", 1)
	setAttr ("defaultResolution.deviceAspectRatio", 1.777)	
	
def Helltools_set720Render ():	
	
	setAttr ("defaultResolution.width", 1280)
	setAttr ("defaultResolution.height", 720)
	setAttr ("defaultResolution.pixelAspect", 1)
	setAttr ("defaultResolution.lockDeviceAspectRatio", 1)
	setAttr ("defaultResolution.deviceAspectRatio", 1.778)	
	
def Helltools_set4KRender ():	
	
	setAttr ("defaultResolution.width", 4096)
	setAttr ("defaultResolution.height", 4096)
	setAttr ("defaultResolution.pixelAspect", 1)
	setAttr ("defaultResolution.lockDeviceAspectRatio", 1)
	setAttr ("defaultResolution.deviceAspectRatio",1)	
	
	
	
#                           #
#  modeling toosl menu      #
#                           #
def primitive_cube():
    cmds.polyCube( sx=1, sy=1, sz=1, w=1,d=1, h=1, cuv=4 ) 

def primitive_plane():
    cmds.polyPlane ( sx=1, sy=1, w=1, h=1, cuv=4 ) 

def primitive_cylinder():
    cmds.polyCylinder( sx=1, sy=1, sz=1, h=2, cuv=4 )
        
def primitive_sphere():
    cmds.polySphere(sx=20, sy=20, r=1)
    
def primitive_torus():
    cmds.polyTorus(sx=20, sy=20, r=1, sr=0.5, tw=0,)

def primitive_pipe():
    cmds.polyPipe( sh=1, h=1 ) 


#                       #
#  outliner   window    #
#                       #

def helltools_outlinerWindow():
    
       
    Outliner = 'Outliner'
    
 
    if cmds.window( 'outlinerWindow', exists=True ):cmds.deleteUI( 'outlinerWindow' )
     
    OutlinerWindow = cmds.window( 'outlinerWindow', title = Outliner, w = 300, h = 500, sizeable = True)
    cmds.frameLayout( labelVisible=False )
    panel = cmds.outlinerPanel()
    Outliner = cmds.outlinerPanel(panel, query=True,outlinerEditor=True)
    cmds.outlinerEditor( Outliner, edit=True, mainListConnection='worldList', selectionConnection='modelList', showShapes=False, showReferenceNodes=False, showReferenceMembers=False, showAttributes=False, showConnected=False, showAnimCurvesOnly=False, autoExpand=False, showDagOnly=True, ignoreDagHierarchy=False, expandConnections=False, showNamespace=True, showCompounds=True, showNumericAttrsOnly=False, highlightActive=True, autoSelectNewObjects=False, doNotSelectNewObjects=False, transmitFilters=False, showSetMembers=True, setFilter='defaultSetFilter' )
    cmds.showWindow()
    
#                          #
#  global UI fimctims    #
#                          #    
    
def helltools_scriptEditor():
    mel.eval('ScriptEditor;')    
    
def helltools_renderEditor():
    mel.eval('unifiedRenderGlobalsWindow;')  

def helltools_attrEditor():
    mel.eval('ToggleAttributeEditor;')

def helltools_toolSettings():
    mel.eval('ToggleToolSettings;')

def helltools_layerChannel():
    mel.eval('ToggleChannelsLayers;')
    
def helltools_graphEditor():
    mel.eval('GraphEditor;')
    
def helltools_cameraSequencer():
    mel.eval('SequenceEditor;')                          
                        
def helltools_polyCount():
    mel.eval('TogglePolyCount;')    
    
def helltools_cameraAttr():
    mel.eval('camAtr;')        

def helltools_clipPlane():
    mel.eval('nfcp;')        
                                                    
def helltools_resolutionGate():
    mel.eval('camera -e -displayFilmGate off -displayResolution on -overscan 1.1 persp;')        

def helltools_restoreUI():
    mel.eval('ShowUIElements;')                                             
                    
                    
               
#               #
#   twin Save   # 
#               #

def HelltoolsTwinSave():
	
	
	ts.Helltools_twinSaveUI()
	               
    
    
    
#                #
#   poly split   #
#                #

def helltools_polySplit():

    mel.eval('setToolTo polySplitContext')
#                   #
#  delete history   #
#                   #    

def helltools_deleteHistory():    
    mel.eval('DeleteHistory')
    
#                    #
#  reset transform   #
#                    #    

def helltools_ResetTransformations():    
    mel.eval('ResetTransformations')
    
#                     #
#  freeze transform   #
#                     #    

def helltools_freezeTransformations():    
    mel.eval('FreezeTransformations')    

#                 #
#  center pivot   #
#                 #    

def helltools_centerPivot ():    
    mel.eval('CenterPivot ') 

#                 #
#  center pivot   #
#                 #    

def helltools_relaxTool ():    
    mel.eval('Relax_Tool') 
    
#                #
#  soften edge   #
#                #    

def helltools_softenEdge ():    
    mel.eval('SoftPolyEdgeElements 1') 
        
#                 #
#  harden Edge    #
#                 #    

def helltools_hardenEdge ():    
    mel.eval('SoftPolyEdgeElements 0') 
        
#                     #
#  normals to face    #
#                     #     

def helltools_toFace ():    
    mel.eval('SetToFaceNormals')     

#                     #
#  reverse to face    #
#                     #     

def helltools_revNormals ():    
    mel.eval('ReversePolygonNormals')       
#                     #
#  reverse to face    #
#                     #     

def helltools_delEdge ():    
    mel.eval('del_edge')  
    
    
    
    
    
def helltools_zPipe():
    
    import zPipeMakerSimple 
    reload(zPipeMakerSimple)
    zPipeMakerSimple.gui()       
    
#                     #
#  curve tools        #
#                     #  

def helltools_CVCurves ():
    mel.eval('CVCurveTool; resetTool curveContextCV;')
    
def helltools_LICurves ():    
    
    mel.eval('CVCurveTool; curveCVCtx -e -d 1 -bez 0 `currentCtx`;')
    
def helltools_BezierCurves ():    
    mel.eval('CreateBezierCurveTool;')    
    
def helltools_3pointArc ():    
    mel.eval('ThreePointArcTool;')
    
def helltools_CurvePen ():    
    mel.eval('PencilCurveTool;')

def helltools_Loc ():    
    mel.eval('CreateLocator;')  
    
    
#                        #
#  Helltools instancer   #
#                        #
def helltools_instanceX():    
    
    mel.eval('''FreezeTransformations;
    	DeleteHistory;
    	instance; scale -r -1 1 1;
    	print("Instance Mirror X Done it"); ''')


def helltools_instanceY():
    mel.eval('''FreezeTransformations;
	    DeleteHistory;
	    instance; scale -r 1 -1 1;
	    print("Instance Mirror Y Done it");''')

def helltools_instanceZ():

	mel.eval('''FreezeTransformations;
	    DeleteHistory;
	    instance; scale -r 1 1 -1;
	    print("Instance Mirror Z Done it");''')

#                       #
#     node unlocker     #
#                       #

def helltools_nodeUnlock():
    mel.eval('lockNode -l 0')    
   

#                       #
#  af Checker window    #
#                       #

def helltools_afChecker():
    mel.eval('af_checkerSd(); shiftCMD;')

def helltools_checkerSize():
    mel.eval('cycCheckerSize;')


#		#
#   file menu   #
#		#

def helltools_openFile():
	mel.eval('OpenScene;')

def helltools_saveScene():

	mel.eval('SaveSceneOptions;')


def helltools_saveSceneAs():

   mel.eval('SaveSceneAs;')
                   

def helltools_exitMaya():
	
    mel.eval('quit;')

def helltools_increment():
    mel.eval('dp_SaveScenePlus') 

#	        	#
#   cleanup menu        #
#	         	#
def helltools_optimizeScene():

	mel.eval("OptimizeSceneOptions;")


def helltools_DelLayer():
    mel.eval('''{
	string $layers[] = `ls -type displayLayer`;
	for($i=1;$i<size($layers);$i++){ 
    	delete $layers[$i]; 
	} 
	}''')
    print('No more layers!')
    

def helltools_dsideOn():
    mel.eval('for($obj in `ls -sl`){ setAttr ($obj+".doubleSided") 1; }')

def helltools_dsideOff():
    mel.eval('for($obj in `ls -sl`){ setAttr ($obj+".doubleSided") 0; }')


#	               	#
#     Asset manager     #
#	         	#



def helltools_assMan():
    mel.eval('craSceneTools;')




#                       #
#  Helltools  window    #
#                       #

#banner

imagePath = cmds.internalVar(upd = True) + "icons/helltools_v2.jpg"

def animBuildUI_importLocalCache():
    
    animBuild_importCache( animBuild_getLocalCacheDir( animBuild_getScenePath() ) )


def animBuildUI_importPublishedCache():
    
    animBuild_importCache( animBuild_getPublishDir( animBuild_getShotSlug ( animBuild_getScenePath() ) ) )


def HelltoolsUI_window():
    
    title  =  '[Helltools' + ' ' + ver + ' ' + ']'
    
   
    if cmds.window( title, q = 1, ex = 1,): deleteUI( title )
    
    animBuilder  =  window( title,mxb = False, t = title, rtf = 1 )
    window( animBuilder, e =.5, wh = ( 245, 720) )
    
    cmds.scrollLayout()

    #animBuildLt = verticalLayout( spacing = 1)
    
    cmds.image(w = 220, h = 80, image = imagePath)
    #cmds.frameLayout( label='Gpu Cache', borderStyle='etchedIn', collapsable=True, collapse=True, bgc = (0.5,0.5,0.0),w=220 )
    #button( 'animBuildBtn_localCache',   l = 'Import Local Cache (Check)', c = Callback( animBuildUI_importLocalCache, borderStyle='in' ) )

    cmds.setParent('..')
    cmds.setParent('..')
    
    cmds.frameLayout( label='File', borderStyle='etchedIn', collapsable=True, collapse = True, bgc = (0.706,0.365,0.157),w=220  )    
    cmds.gridLayout(numberOfColumns = 2 ,cellWidth=108)
    
    button( 'helltools_open',   l = 'Open File',  c = Callback( helltools_openFile ) )
    button( 'helltools_save',   l = 'Save Scene',  c = Callback( helltools_saveScene ) )
    button( 'helltools_saveAs',   l = 'Save As',  c = Callback( helltools_saveSceneAs) )
    button( 'helltools_incrementalSave',   l = 'Incremental Save',  c = Callback( helltools_increment ) )





    cmds.setParent('..')
    cmds.setParent('..')
    
    cmds.frameLayout( label='Primitives', borderStyle='etchedIn', collapsable=True, collapse = True, bgc = (0.706,0.365,0.157),w=220  )

    cmds.frameLayout( label='Polygons', borderStyle='etchedIn', collapsable=False, collapse = False, bgc = (0.141,0.141,0.141),w=220  )
    cmds.gridLayout(numberOfColumns = 2 ,cellWidth=108)
    
      
    button( 'primitiveTools_Cube',   l = 'Create Cube',  c = Callback( primitive_cube ) )
    button( 'primitiveTools_Plane',   l = 'Create Plane',  c = Callback( primitive_plane ) )
    button( 'primitiveTools_Cylinder',   l = 'Create Cylinder',  c = Callback( primitive_cylinder ) )
    button( 'primitiveTools_Sphere',   l = 'Create Sphere',  c = Callback( primitive_sphere ) )
    button( 'primitiveTools_Torus',   l = 'Create Torus',  c = Callback( primitive_torus ) )
    button( 'primitiveTools_Pipe',   l = 'Create Pipe',  c = Callback( primitive_pipe ) )
    
    cmds.setParent('..')
    cmds.setParent('..')
    
    cmds.frameLayout( label='Curves', borderStyle='etchedIn', collapsable=False, collapse = False, bgc = (0.141,0.141,0.141),w=220  )
    cmds.gridLayout(numberOfColumns = 2,cellWidth=108)
      
    button( 'nurbTools_CVC',   l = 'CV Curve',  c = Callback( helltools_CVCurves ) )
    button( 'nurbTools_LIC',   l = 'LI Curve',  c = Callback( helltools_LICurves ) )
    button( 'nurbTools_BezC',   l = 'Bezier Curve',  c = Callback( helltools_BezierCurves ) )
    button( 'nurbTools_CurvePen',   l = 'Curve Pen',  c = Callback( helltools_CurvePen ) )
    button( 'nurbTools_3pArc',   l = '3 Point Arc',  c = Callback( helltools_3pointArc ) )
    button( 'nurbTools_Loc',   l = 'Locator',  c = Callback( helltools_Loc ) )

    cmds.setParent('..')
    cmds.setParent('..')
    
    
    cmds.setParent('..')
    cmds.setParent('..')
    
    cmds.frameLayout( label='Modeling Tools', borderStyle='in', collapsable=True, collapse = True, bgc = (0.706,0.365,0.157),w=220 )  
    
    cmds.gridLayout(numberOfColumns = 2,cellWidth=108)
    
    button('hellTools_polySplit',   l = 'Split Poly',  c = Callback( helltools_polySplit ) )
    button('helltools_deleteHistory', l= 'Delete History', c = Callback( helltools_deleteHistory) )
    button('helltools_ResetTransformations', l= 'Reset Xform', c = Callback( helltools_ResetTransformations) )
    button('helltools_freezeTransformations', l= 'Freeze Xform', c = Callback( helltools_freezeTransformations) )
    button('helltools_centerPivot', l= 'Center Pivot', c = Callback( helltools_centerPivot) )
    button('helltools_relaxTool', l= 'Relax Tool', c = Callback( helltools_relaxTool) )
    button('helltools_softenEdge', l= 'Soft Edges', c = Callback( helltools_softenEdge) )
    button('helltools_hardenEdge', l= 'Hard Edges', c = Callback( helltools_hardenEdge) )
    button('helltools_toFace', l= 'set normals to face', c = Callback( helltools_toFace) )
    button('helltools_revNorms', l= 'Reverse Normals', c = Callback( helltools_revNormals) )
    button('helltools_delEdge', l= 'Delete Edge', c = Callback( helltools_delEdge) )
    button('helltools_zPipe', l= 'Z Pipe Maker', c = Callback( helltools_zPipe ) )
   
    cmds.setParent('..')
    cmds.gridLayout(numberOfColumns = 3,cellWidth=72)
   
    button('helltools_instX', l= 'InstanceX', c = Callback( helltools_instanceX ) )
    button('helltools_instY', l= 'InstanceY', c = Callback( helltools_instanceY ) )
    button('helltools_instZ', l= 'InstanceZ', c = Callback( helltools_instanceZ ) )
   
   
   
    cmds.setParent('..')
    cmds.setParent('..')
    
    cmds.frameLayout( label='Setup', borderStyle='in', collapsable=True, collapse = False, bgc = (0.706,0.365,0.157),w=220  )  
    
    cmds.frameLayout( label='Render Settings', borderStyle='etchedIn', collapsable=False, collapse = False, bgc = (0.141,0.141,0.141),w=220  )
    cmds.gridLayout(numberOfColumns = 2 ,cellWidth=108)

    button( 'helltools_Render720Btn',   l = 'Set Render settings 720',  c = Callback( Helltools_set720Render ) )
    button( 'helltools_Render1080Btn',   l = 'Set Render settings 1080',  c = Callback( Helltools_set1080Render ) )
    button( 'helltools_RenderSettingsBtn',   l = 'Set Render Settings 2K',  c = Callback( Helltools_set2KRender ) )
    button( 'helltoolsn_4kSettingsBtn',   l = 'Set Render Settings 4K',  c = Callback( Helltools_set4KRender ) )
    

    cmds.setParent('..')
    cmds.setParent('..')
    
    cmds.frameLayout( label='Create Hierarchy', borderStyle='etchedIn', collapsable=False, collapse = False, bgc = (0.141,0.141,0.141),w=220  )
    cmds.gridLayout(numberOfColumns = 2 ,cellWidth=108)
    
    button( 'animBuildBtn_buildCharHierarchy', l = 'Build Char. Hierarchy', c = Callback(Helltools_createCharacterHierarchy ) )
    button( 'animBuildBtn_buildPrHierarchy', l = 'Build Props Hierarchy', c = Callback(Helltools_createPropsHierarchy ) )
    button( 'animBuildBtn_createGroups',  l = 'SSU Hierarchy', c = Callback( animBuild_createSsuHierarchy ) )
    button( 'animBuildBtn_createSTDs',  l = 'STD Hierarchy', c = Callback( animBuild_createStdHierarchy ) )
    button( 'animBuildBtn_createNewSSU',  l = 'New SSU(tmp)', c = Callback( Helltools_newSSUHierarchy ) )
    button( 'animBuildBtn_createNewSTDs',  l = 'New STD(tmp)', c = Callback( Helltools_newSTDHierarchy  ) )
    


    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')

    cmds.frameLayout( label='Global UI', borderStyle='in', collapsable=True, collapse=True, bgc = (0.706,0.365,0.157),w=220  )
    cmds.gridLayout(numberOfColumns = 3, cellWidth=72)
    
    button( 'helltools_outliner_button',  l = 'Outliner', c = Callback( helltools_outlinerWindow ),)
    button( 'helltools_scriptEditor_button',  l = 'Script Editor', c = Callback( helltools_scriptEditor ) )
    button( 'helltools_renderEditor_button',  l = 'Render Set.', c = Callback( helltools_renderEditor ) )
    button( 'helltools_attrEditor_button',  l = 'Attr Editor', c = Callback( helltools_attrEditor ) )
    button( 'helltools_toolSettings_button',  l = 'Tool Settings', c = Callback( helltools_toolSettings ) )
    button( 'helltools_layerChannel_buttton',  l = 'Layer/Chans', c = Callback( helltools_layerChannel ) )
    button( 'helltools_cameraSequencer_button',  l = 'Sequencer', c = Callback( helltools_cameraSequencer ) )
    button( 'helltools_polyCount_button',  l = 'Polycount', c = Callback( helltools_polyCount ) )
    button( 'helltools_cameraAttr_button',  l = 'Camera Attr', c = Callback( helltools_cameraAttr ) ) 
    button( 'helltools_clipPlane_button',  l = 'Clip Plane', c = Callback( helltools_clipPlane ) ) 
    button( 'helltools_resolutionGate_button',  l = 'Reso Gate', c = Callback( helltools_resolutionGate ) ) 
    button( 'helltools_restoreUI_button',  l = 'Restore UI', c = Callback( helltools_restoreUI ) ) 
     
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')

    cmds.frameLayout( label='Clean Up', borderStyle='in', collapsable=True, collapse=True, bgc = (0.706,0.365,0.157),w=220  )
    cmds.gridLayout(numberOfColumns = 2 ,cellWidth=108)   

    button( 'helltools_optimizeMe',  l = 'Optimize Scene', c = Callback( helltools_optimizeScene ) )
    button( 'helltools_deleteLayer',  l = 'Delete Layers', c = Callback( helltools_DelLayer ) )
    button( 'helltools_doubleSideOn',  l = 'Double sided ON', c = Callback( helltools_dsideOn ) )
    button( 'helltools_doubleSideOff',  l = 'Double sided OFF', c = Callback( helltools_dsideOff ) )
   


    cmds.setParent('..')
    cmds.setParent('..')
    
    cmds.frameLayout( label='Utilities', borderStyle='in', collapsable=True, collapse=False, bgc = (0.706,0.365,0.157),w=220  )
    cmds.gridLayout(numberOfColumns = 2,cellWidth=108)

    button( 'animBuildBtn_createLocs',   l = 'Locators On Selection',    c = Callback( animBuild_locatorOnTarget ) )
    button( 'animBuildBtn_posFromLocs',  l = 'Get Pos from Locators',   c = Callback( animBuild_retrieveFromLocators ) )
    button( 'animBuildBtn_localCache',   l = 'Import GPU Cache', c = Callback( animBuildUI_importLocalCache ) )
    button( 'helltools_nodeUnlocker',  l = 'Unlock Node',   c = Callback( helltools_nodeUnlock ) )
    
    cmds.setParent('..')
    cmds.setParent('..')
    
    
    cmds.frameLayout( label='External Tools', borderStyle='in', collapsable=True, collapse=False, bgc = (0.706,0.365,0.157),w=220  )
    
    button( ' helltools_cometrename',   l = 'CometRename',    c = Callback(  helltools_cometRename ) )
    button( 'helltools_nightShade',  l = 'NightSahde UV Editor',   c = Callback( helltools_nightShadeUV ) )
    button( 'helltools_assetManager',  l = 'Asset Manager',   c = Callback( helltools_assMan ) )   
    button( 'helltools_AFcheckSize',  l = "Hell's Twin Save",   c = Callback( HelltoolsTwinSave ) )

    cmds.frameLayout( label='AF Checker', borderStyle='etchedIn', collapsable=False, collapse = False, bgc = (0.141,0.141,0.141),w=220  )
    cmds.gridLayout(numberOfColumns = 2 ,cellWidth=108)     
    
    button( 'helltools_AFcheckON',  l = 'Load checker',   c = Callback( helltools_afChecker ) )
    button( 'helltools_AFcheckSize',  l = 'Checker Size',   c = Callback( helltools_checkerSize ) )
	

    #animBuildLt.redistribute(.5, .5, .5, .5, .5, .5, .5, .5, .5)
    showWindow( animBuilder )

HelltoolsUI_window()

# base code from Romain Cabanier, edit and modified  by jp marchand  #