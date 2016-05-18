from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from pandac.PandaModules import Material
from pandac.PandaModules import VBase4
from pandac.PandaModules import WindowProperties
from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from panda3d.core import CollisionTraverser,CollisionNode
from panda3d.core import CollisionHandlerQueue,CollisionRay,CollisionHandlerEvent
from panda3d.core import Vec3,Vec4,BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *

class MyApp(ShowBase):
   def __init__(self):
      ShowBase.__init__(self)

      self.imageObject = OnscreenImage(image = 'earth.jpg', pos = (0, 1, 0))
      self.imageObject.setScale(1.9,1,1)
      tpRed = TextProperties()
      tpRed.setTextColor(1, 1, 1, 1)
      tpSlant = TextProperties()
      tpSlant.setSlant(0.3)
      tpRoman = TextProperties()
      cmr12 = loader.loadFont('cmr12.egg')
      tpRoman.setFont(cmr12)
      tpMgr = TextPropertiesManager.getGlobalPtr()
      tpMgr.setProperties("red", tpRed)
      tpMgr.setProperties("slant", tpSlant)
      tpMgr.setProperties("roman", tpRoman)
      self.textObject = OnscreenText(text = '\1red\1\1roman\1\1slant\1Space Collector', pos = (-0.6, 0.4), scale = 0.2)
      self.textScore=0



      self.b = DirectButton(text = ("Start", "Start", "Start", "disabled"),command=self.beginGame)	
      self.b.setScale(0.1,0.1,0.1)
      self.b.setPos(0.7,0,-0.8)

      myMaterial = Material()
      myMaterial.setShininess(1000)
      myMaterial.setDiffuse(VBase4(0.5,0.5,0.5,1))
      myMaterial.setAmbient(VBase4(5,5,5,1))
      myMaterial.setSpecular(VBase4(10,10,10,1))

      myTexture = loader.loadTexture("maps/grayjumpjetTexture.tif")

      self.ship = loader.loadModel("GrayJumpJet")
      self.ship.setScale(0.15, 0.3, 0.15)
      self.ship.setPos(0,0,0)
      self.ship.setTexture(myTexture,1)
      self.ship.reparentTo(render)

      self.slab = loader.loadModel("box")
      self.slab.find("**/Cube;+h").setCollideMask(BitMask32.bit(0))
      self.slab.setScale(1.5,10,1)
      self.slab.setPos(0,0,-1)
      self.slab.setHpr(0,0,0)
      self.slab.setMaterial(myMaterial)
      self.slab.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
      self.slab.setTexProjector(TextureStage.getDefault(), render, self.slab)
      self.slab.setTexture(loader.loadTexture("maps/crate_Material_#11_CL.tif"),1)
      self.junk = [None]*100
      self.loadJunk()


      self.createTrack()

      base.trackball.node().setPos(0, 20, -4)

      self.acceleration=0
      self.velocity=0
      self.yPos=0

      render.setShaderAuto()

      self.cTrav = CollisionTraverser()

      self.shipGroundRay = CollisionRay()
      self.shipGroundRay.setOrigin(0,0,1000)
      self.shipGroundRay.setDirection(0,0,-1)
      self.shipGroundCol = CollisionNode('shipRay')
      self.shipGroundCol.addSolid(self.shipGroundRay)
      self.shipGroundCol.setFromCollideMask(BitMask32.bit(0))
      self.shipGroundCol.setIntoCollideMask(BitMask32.allOff())
      self.shipGroundColNp = self.ship.attachNewNode(self.shipGroundCol)
      self.shipGroundHandler = CollisionHandlerQueue()
      self.cTrav.addCollider(self.shipGroundColNp, self.shipGroundHandler)
      self.collHandEvent = CollisionHandlerEvent()        
      # add the into pattern with fromObject-into-thisObject        
      self.collHandEvent.addInPattern( 'into-%in' )
      self.accept("into-Junk",self.cHandler)
      bkground = loader.loadModel("square")
      bkground.reparentTo(camera)
      bkground.setScale(300,170,50)
      tex = loader.loadTexture("earth2.jpg")
      bkground.setTexture(tex,1)
      bkground.setPos(0,299,0)
      bkground.setHpr(0,90,0)
      base.camLens.setFar(300)

      self.mySound = loader.loadMusic("coinslot1.wav")
      self.timer=60
      self.textTimer=0
      self.prevY=0
      self.prevX=0
      self.shipGroundColNp.show()
      #self.camGroundColNp.show()
      self.collided=1
      self.jumpTime=0
      self.jumpOn=0
      self.curZ=0
      self.interval=0
      self.zPosition=0
      self.isGameOver=0
      self.score=0
      # Uncomment this line to show a visual representation of the 
      # collisions occuring
      #self.cTrav.showCollisions(render)
      if base.mouseWatcherNode.hasMouse():
             self.prevX=base.mouseWatcherNode.getMouseX()
             self.prevY=base.mouseWatcherNode.getMouseY()

   def beginGame(self):
      self.textObject.destroy()
      self.imageObject.destroy()
      self.b.destroy()
      props = WindowProperties()
      props.setCursorHidden(True)
      base.win.requestProperties(props)
      self.taskMgr.add(self.moveForward, "MoveForward")
      self.accept("mouse1",self.jump)
      self.textScore = OnscreenText(text = '\1red\1\1slant\1Score : 0', pos = (-0.8, 0.8), scale = 0.1)
      self.textTimer = OnscreenText(text = '\1red\1\1slant\1Time Left : 2:00', pos = (-0.8, 0.7), scale = 0.1)
      print 'GameBegin'


   def cHandler(self,collEntry):
      print "collision"

   def loadJunk(self):
      f = open('junk1.txt','r')
      x=f.readline()
      y=f.readline()
      z=f.readline()
      i=0
      while x!="":
             self.junk[i] = loader.loadModel("rubbishset/rubbish-set.lwo")
             self.junk[i].setScale(0.5,1,0.5)
             self.junk[i].reparentTo(render)
             colSphere=self.initCollisionSphere(self.junk[i],"Junk")
             self.junk[i].setPos(int(x),int(y),int(z))
             x=f.readline()
             y=f.readline()
             z=f.readline()
             i=i+1
                 
                
   def initCollisionSphere(self,node,name):
      bounds = node.getBounds()
      center = bounds.getCenter()
      radius = bounds.getRadius()*0.6
      cNode = CollisionNode(name)
      cNode.addSolid(CollisionSphere(center,radius))
      cNP=node.attachNewNode(cNode)
      cNP.show()
      return cNP

   def createTrack(self):
      f = open('track.txt','r')
      a = f.read(1)
      i=0
      j=0
      while(a!=""):
         if a=="\n":
            a=f.read(1)
         if(a==""):
            break
         nSlab = int(a)
         #print nSlab
         while nSlab!=0:
            placeholder = render.attachNewNode("Slab")
            placeholder.setColor(j*0.92*0.4,nSlab*nSlab*0.51,0.23,1)
            placeholder.setPos(j*3-7,i*15,nSlab-3)
            self.slab.instanceTo(placeholder)
            nSlab=nSlab-1
         j=j+1
         if(j==5):
            i=i+1
            j=0
            print i
         a=f.read(1)
                             

   def moveForward(self, task):
      curX=0
      curY=0
      shipCollided=0
      c=self.timer-int(task.time)
      self.textTimer.setText('\1red\1\1slant\1Time Left : '+str(int(c/60))+':'+str(c%60))
      if base.mouseWatcherNode.hasMouse():
          curX=base.mouseWatcherNode.getMouseX()
          curY=base.mouseWatcherNode.getMouseY()
      #if(curY>self.prevY+0.01):
      self.acceleration = self.acceleration+1
      #if(curY<self.prevY-0.01):
      #	self.acceleration = self.acceleration-1

      if(self.acceleration<45 and self.acceleration>=0):
          self.velocity=self.acceleration*task.time

      self.yPos=self.velocity * task.time
      self.ship.setY(self.yPos)

      if self.prevX<curX-0.001:
          self.ship.setHpr(0,0,5)
          #Sequence(self.ship.hprInterval(0.1,Point3(0,0,10),self.ship.getHpr())).start()
          self.ship.setX(curX*8)
          self.prevX=curX
      elif self.prevX>curX+0.001:
          self.ship.setHpr(0,0,-5)
          #Sequence(self.ship.hprInterval(0.1,Point3(0,0,-10),self.ship.getHpr())).start()
          self.ship.setX(curX*8)
          self.prevX=curX
      else:
          #self.ship.setHpr(0,0,0)
          Sequence(self.ship.hprInterval(0.1,Point3(0,0,0),self.ship.getHpr())).start()

      #print yPos
      self.camera.setPos(0,self.yPos-25,4)
      #self.slnp.setPos(0,self.yPos+20,4)
      self.cTrav.traverse(render)

      entries = []
      for i in range(self.shipGroundHandler.getNumEntries()):
         entry = self.shipGroundHandler.getEntry(i)
         entries.append(entry)
      entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                  x.getSurfacePoint(render).getZ()))
      if (len(entries)>0) and (entries[0].getIntoNode().getName() == "Cube"):
         self.zPosition=entries[0].getSurfacePoint(render).getZ()
         #self.ship.setZ(entries[0].getSurfacePoint(render).getZ()+1)
         print str(self.zPosition) + " "+str(self.ship.getZ())
         if self.zPosition>=self.ship.getZ():
            shipCollided=1
            self.isGameOver=1
         else:
            shipCollided=0
         self.collided=1
         print entries[0].getIntoNode().getName() + "collided"
      elif (len(entries)>0) and (entries[0].getIntoNode().getName() == "Junk"):
         pZ=entries[0].getSurfacePoint(render).getZ()
         if(self.ship.getZ()<=pZ and self.ship.getZ()>=pZ-2):
            entries[0].getIntoNode().getParent(0).removeAllChildren()
            self.score=self.score+1000
            self.timer=self.timer+20
            self.textScore.setText('\1red\1\1slant\1Score : '+str(self.score))
            self.mySound.play()
            print self.score 
      else:
         self.collided=0
      if shipCollided!=1:
         val=0
         if(self.jumpOn==1):
            val=10
         if(self.interval==0):
            self.interval=task.time
            self.curZ=self.ship.getZ()
            self.jumpTime=0
         else:
            self.jumpTime=self.jumpTime+task.time-self.interval
            self.interval=task.time
            zPos = self.curZ + val*self.jumpTime - 12*self.jumpTime*self.jumpTime
            if(zPos<self.zPosition+1 and self.collided==1):
               zPos=self.zPosition+1
               self.ship.setZ(zPos)
               self.accept("mouse1",self.jump)
               self.jumpOn=0
               self.interval=0
            else:
               self.ship.setZ(zPos)
               if zPos<-40:
                  self.isGameOver=1
                             
      self.prevX=curX
      self.prevY=curY
      self.score=self.score+1
      self.textScore.setText('\1red\1\1slant\1Score : '+str(self.score))
      if(self.isGameOver==1):
         props = WindowProperties()
         props.setCursorHidden(False)
         base.win.requestProperties(props)
         self.imageObject = OnscreenImage(image = 'earth.jpg', pos = (0, 1, 0))
         self.imageObject.setScale(1.9,1,1)
         self.textObject = OnscreenText(text = '\1red\1\1roman\1\1slant\1Space Collector', pos = (-0.6, 0.4), scale = 0.2)
         self.b = DirectButton(text = ("Start", "Start", "Start", "disabled"),command=self.beginGame)
         self.b.setScale(0.1,0.1,0.1)
         self.b.setPos(0.7,0,-0.8)
         self.ship.setPos(0,0,0)
         self.zPosition=0
         self.prevY=0
         self.prevX=0
         self.collided=1
         self.jumpTime=0
         self.jumpOn=0
         self.curZ=0
         self.interval=0
         self.zPosition=0
         self.isGameOver=0
         self.score=0
         self.acceleration=0
         self.velocity=0
         self.yPos=0
         self.score=0
         self.timer=120
         self.textTimer.destroy()
         self.textScore.destroy()
         for x in self.junk:
               if(x!=None):
                       x.detachNode()
                       x=None
                       print 'destroyed'
         self.loadJunk()
      else:
         return Task.cont

   def jump(self):
      self.jumpOn=1
      self.ignore("mouse1")

def beginGame():
   print 'pressed'

app = MyApp()
app.run()
