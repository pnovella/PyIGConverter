
from Centella.AAlgo import AAlgo
from Centella.physical_constants import *
from Centella.gateWriter import gateWriter
from Centella.cerrors import *

from ROOT import gSystem

ok = gSystem.Load("$GATE_DIR/lib/libGATE")

if not ok: raise CImportError("GATE_LIB path not defined!")

from ROOT import gate

class IGConverter(AAlgo):

    def __init__(self,param=False,level = 1,label="",**kargs):

        """
        Initialize members and take input arguments
        """
        
        self.name='IGConverter'
        
        self.writer = gateWriter()

        AAlgo.__init__(self,param,level,self.name,0,label,kargs)
        
        try: self.dstname = self.strings["GATE_DST_NAME"]
        
        except KeyError: self.dstname = "irene2gate.root" 

    def initialize(self):

        """
        Create writer for gate DST
        """
        
        self.m.log(1,'+++Init method of IGConverter algorithm+++')
        
        self.writer.open(self.dstname)

        return

    def execute(self,event=""):

        """
        Convert irene events into gate events and save into DST
        """

        gevent = self.irene2gate(event)
        
        self.writer.write(gevent,0)

        return True
        
    def irene2gate(self,event):
        
        gevent = gate.Event()
        
        gevent.SetID( event.GetID() )
        
        tparts = event.GetParticles()
        
        pIDs = {}

        for part in tparts:
            
            gpart = gate.MCParticle()
            
            gpart.SetPDG( part.GetPDGcode() )
            
            gpart.SetPrimary( part.IsPrimary() )

            gpart.SetID( part.GetParticleID() )
            
            pIDs[part.GetParticleID()] = gpart

            daus = part.GetDaughters()
            
            dausIDv = gate.vint()
            
            for i in range(daus.GetEntriesFast()): 

                dausIDv.push_back(daus[i].GetParticleID())

            gpart.store("dausID",dausIDv)
            
            if not part.IsPrimary(): 
                
                gpart.store("momID",part.GetMother().GetParticleID())
                
            mom = part.GetInitialMomentum()

            gpart.SetInitialMom(mom.X(),mom.Y(),mom.Z(),mom.E())

            mom = part.GetDecayMomentum()

            gpart.SetFinalMom(mom.X(),mom.Y(),mom.Z(),mom.E())

            vtx = part.GetInitialVertex()
            
            gpart.SetInitialVtx(vtx.X(),vtx.Y(),vtx.Z())
            
            vtx = part.GetDecayVertex()
            
            gpart.SetFinalVtx(vtx.X(),vtx.Y(),vtx.Z())
            
            gevent.AddMCParticle(gpart)
            
            for itrk in range(part.GetTracks().GetEntriesFast()): 
                
                trk = part.GetTracks()[itrk]

                gtrk = gate.MCTrack()
                
                gtrk.SetParticle(gpart)
                
                gpart.AddTrack(gtrk) # Add to particle

                gevent.AddMCTrack(gtrk) # add to event
                
                for hit in trk.GetHits():
                    
                    ghit = gate.MCHit()
                    
                    ghit.SetParticle(gpart)
                    
                    ghit.SetAmplitude(hit[1])
                    
                    ghit.SetPosition(hit[0].X(),hit[0].Y(),hit[0].Z())

                    gtrk.AddHit(ghit)
                    
                    gevent.AddMCHit(ghit)
        
        
        
        for part in gevent.GetMCParticles():
            
            dausID = part.fetch_ivstore("dausID")

            for dauID in dausID: part.AddDaughter(pIDs[dauID])
            
            part.erase_ivstore("dausID")

            if not part.IsPrimary(): 
                
                part.SetMother(pIDs[part.fetch_istore("momID")])
        
                part.erase_istore("momID")

        #for part in gevent.GetMCParticles():
        #    print "ID:",part.GetID()
        #    if not part.IsPrimary(): print "Mom ID:",part.fetch_istore("momID")
        #    dausID = part.fetch_ivstore("dausID")
        #    print "dau IDs:",[ dausID[i] for i in  range(dausID.size())]
            
        #gevent.Info()

        return gevent

    def finalize(self):

        
        self.m.log(1,'+++End method of IGConverter algorithm+++')
        
        self.writer.close()

        return

    
