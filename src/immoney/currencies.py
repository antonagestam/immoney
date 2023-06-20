from __future__ import annotations

from typing import Final
from typing import final

from . import Currency
from .registry import CurrencyCollector
from .registry import CurrencyRegistry

__currencies: Final = CurrencyCollector[Currency]()


@final
class ADPType(Currency):
    code = "ADP"
    subunit = 1


ADP: Final = ADPType()
__currencies.add(ADP)


@final
class AFAType(Currency):
    code = "AFA"
    subunit = 100


AFA: Final = AFAType()
__currencies.add(AFA)


@final
class ALKType(Currency):
    code = "ALK"
    subunit = 1


ALK: Final = ALKType()
__currencies.add(ALK)


@final
class AONType(Currency):
    code = "AON"
    subunit = 1


AON: Final = AONType()
__currencies.add(AON)


@final
class AORType(Currency):
    code = "AOR"
    subunit = 1


AOR: Final = AORType()
__currencies.add(AOR)


@final
class ARAType(Currency):
    code = "ARA"
    subunit = 100


ARA: Final = ARAType()
__currencies.add(ARA)


@final
class ARPType(Currency):
    code = "ARP"
    subunit = 100


ARP: Final = ARPType()
__currencies.add(ARP)


@final
class ATSType(Currency):
    code = "ATS"
    subunit = 100


ATS: Final = ATSType()
__currencies.add(ATS)


@final
class AZMType(Currency):
    code = "AZM"
    subunit = 100


AZM: Final = AZMType()
__currencies.add(AZM)


@final
class BADType(Currency):
    code = "BAD"
    subunit = 100


BAD: Final = BADType()
__currencies.add(BAD)


@final
class BEFType(Currency):
    code = "BEF"
    subunit = 100


BEF: Final = BEFType()
__currencies.add(BEF)


@final
class BGLType(Currency):
    code = "BGL"
    subunit = 100


BGL: Final = BGLType()
__currencies.add(BGL)


@final
class BRCType(Currency):
    code = "BRC"
    subunit = 100


BRC: Final = BRCType()
__currencies.add(BRC)


@final
class BREType(Currency):
    code = "BRE"
    subunit = 100


BRE: Final = BREType()
__currencies.add(BRE)


@final
class BRNType(Currency):
    code = "BRN"
    subunit = 100


BRN: Final = BRNType()
__currencies.add(BRN)


@final
class BRRType(Currency):
    code = "BRR"
    subunit = 100


BRR: Final = BRRType()
__currencies.add(BRR)


@final
class BYRType(Currency):
    code = "BYR"
    subunit = 1


BYR: Final = BYRType()
__currencies.add(BYR)


@final
class CLEType(Currency):
    code = "CLE"
    subunit = 1


CLE: Final = CLEType()
__currencies.add(CLE)


@final
class CSDType(Currency):
    code = "CSD"
    subunit = 100


CSD: Final = CSDType()
__currencies.add(CSD)


@final
class CSKType(Currency):
    code = "CSK"
    subunit = 1


CSK: Final = CSKType()
__currencies.add(CSK)


@final
class CYPType(Currency):
    code = "CYP"
    subunit = 100


CYP: Final = CYPType()
__currencies.add(CYP)


@final
class DDMType(Currency):
    code = "DDM"
    subunit = 1


DDM: Final = DDMType()
__currencies.add(DDM)


@final
class DEMType(Currency):
    code = "DEM"
    subunit = 100


DEM: Final = DEMType()
__currencies.add(DEM)


@final
class ECSType(Currency):
    code = "ECS"
    subunit = 1


ECS: Final = ECSType()
__currencies.add(ECS)


@final
class ECVType(Currency):
    code = "ECV"
    subunit = 100


ECV: Final = ECVType()
__currencies.add(ECV)


@final
class EEKType(Currency):
    code = "EEK"
    subunit = 100


EEK: Final = EEKType()
__currencies.add(EEK)


@final
class ESAType(Currency):
    code = "ESA"
    subunit = 1


ESA: Final = ESAType()
__currencies.add(ESA)


@final
class ESBType(Currency):
    code = "ESB"
    subunit = 1


ESB: Final = ESBType()
__currencies.add(ESB)


@final
class ESPType(Currency):
    code = "ESP"
    subunit = 1


ESP: Final = ESPType()
__currencies.add(ESP)


@final
class FIMType(Currency):
    code = "FIM"
    subunit = 100


FIM: Final = FIMType()
__currencies.add(FIM)


@final
class FRFType(Currency):
    code = "FRF"
    subunit = 100


FRF: Final = FRFType()
__currencies.add(FRF)


@final
class GHCType(Currency):
    code = "GHC"
    subunit = 100


GHC: Final = GHCType()
__currencies.add(GHC)


@final
class GRDType(Currency):
    code = "GRD"
    subunit = 100


GRD: Final = GRDType()
__currencies.add(GRD)


@final
class GWPType(Currency):
    code = "GWP"
    subunit = 100


GWP: Final = GWPType()
__currencies.add(GWP)


@final
class HRDType(Currency):
    code = "HRD"
    subunit = 100


HRD: Final = HRDType()
__currencies.add(HRD)


@final
class IEPType(Currency):
    code = "IEP"
    subunit = 100


IEP: Final = IEPType()
__currencies.add(IEP)


@final
class ITLType(Currency):
    code = "ITL"
    subunit = 1


ITL: Final = ITLType()
__currencies.add(ITL)


@final
class LTLType(Currency):
    code = "LTL"
    subunit = 100


LTL: Final = LTLType()
__currencies.add(LTL)


@final
class LUFType(Currency):
    code = "LUF"
    subunit = 100


LUF: Final = LUFType()
__currencies.add(LUF)


@final
class LVLType(Currency):
    code = "LVL"
    subunit = 100


LVL: Final = LVLType()
__currencies.add(LVL)


@final
class MGFType(Currency):
    code = "MGF"
    subunit = 1


MGF: Final = MGFType()
__currencies.add(MGF)


@final
class MLFType(Currency):
    code = "MLF"
    subunit = 1


MLF: Final = MLFType()
__currencies.add(MLF)


@final
class MROType(Currency):
    code = "MRO"
    subunit = 100


MRO: Final = MROType()
__currencies.add(MRO)


@final
class MTLType(Currency):
    code = "MTL"
    subunit = 100


MTL: Final = MTLType()
__currencies.add(MTL)


@final
class MZMType(Currency):
    code = "MZM"
    subunit = 100


MZM: Final = MZMType()
__currencies.add(MZM)


@final
class NLGType(Currency):
    code = "NLG"
    subunit = 100


NLG: Final = NLGType()
__currencies.add(NLG)


@final
class PEIType(Currency):
    code = "PEI"
    subunit = 1


PEI: Final = PEIType()
__currencies.add(PEI)


@final
class PLZType(Currency):
    code = "PLZ"
    subunit = 100


PLZ: Final = PLZType()
__currencies.add(PLZ)


@final
class PTEType(Currency):
    code = "PTE"
    subunit = 1


PTE: Final = PTEType()
__currencies.add(PTE)


@final
class ROLType(Currency):
    code = "ROL"
    subunit = 1


ROL: Final = ROLType()
__currencies.add(ROL)


@final
class RURType(Currency):
    code = "RUR"
    subunit = 100


RUR: Final = RURType()
__currencies.add(RUR)


@final
class SDDType(Currency):
    code = "SDD"
    subunit = 100


SDD: Final = SDDType()
__currencies.add(SDD)


@final
class SITType(Currency):
    code = "SIT"
    subunit = 100


SIT: Final = SITType()
__currencies.add(SIT)


@final
class SKKType(Currency):
    code = "SKK"
    subunit = 100


SKK: Final = SKKType()
__currencies.add(SKK)


@final
class SRGType(Currency):
    code = "SRG"
    subunit = 100


SRG: Final = SRGType()
__currencies.add(SRG)


@final
class STDType(Currency):
    code = "STD"
    subunit = 100


STD: Final = STDType()
__currencies.add(STD)


@final
class TJRType(Currency):
    code = "TJR"
    subunit = 1


TJR: Final = TJRType()
__currencies.add(TJR)


@final
class TMMType(Currency):
    code = "TMM"
    subunit = 100


TMM: Final = TMMType()
__currencies.add(TMM)


@final
class TPEType(Currency):
    code = "TPE"
    subunit = 1


TPE: Final = TPEType()
__currencies.add(TPE)


@final
class TRLType(Currency):
    code = "TRL"
    subunit = 1


TRL: Final = TRLType()
__currencies.add(TRL)


@final
class UAKType(Currency):
    code = "UAK"
    subunit = 100


UAK: Final = UAKType()
__currencies.add(UAK)


@final
class USSType(Currency):
    code = "USS"
    subunit = 100


USS: Final = USSType()
__currencies.add(USS)


@final
class VEBType(Currency):
    code = "VEB"
    subunit = 100


VEB: Final = VEBType()
__currencies.add(VEB)


@final
class VEFType(Currency):
    code = "VEF"
    subunit = 100


VEF: Final = VEFType()
__currencies.add(VEF)


@final
class VNNType(Currency):
    code = "VNN"
    subunit = 1


VNN: Final = VNNType()
__currencies.add(VNN)


@final
class XEUType(Currency):
    code = "XEU"
    subunit = 1


XEU: Final = XEUType()
__currencies.add(XEU)


@final
class YDDType(Currency):
    code = "YDD"
    subunit = 1


YDD: Final = YDDType()
__currencies.add(YDD)


@final
class YUMType(Currency):
    code = "YUM"
    subunit = 100


YUM: Final = YUMType()
__currencies.add(YUM)


@final
class YUNType(Currency):
    code = "YUN"
    subunit = 100


YUN: Final = YUNType()
__currencies.add(YUN)


@final
class ZALType(Currency):
    code = "ZAL"
    subunit = 100


ZAL: Final = ZALType()
__currencies.add(ZAL)


@final
class ZMKType(Currency):
    code = "ZMK"
    subunit = 100


ZMK: Final = ZMKType()
__currencies.add(ZMK)


@final
class ZRNType(Currency):
    code = "ZRN"
    subunit = 100


ZRN: Final = ZRNType()
__currencies.add(ZRN)


@final
class ZRZType(Currency):
    code = "ZRZ"
    subunit = 100


ZRZ: Final = ZRZType()
__currencies.add(ZRZ)


@final
class ZWDType(Currency):
    code = "ZWD"
    subunit = 100


ZWD: Final = ZWDType()
__currencies.add(ZWD)


@final
class ZWLType(Currency):
    code = "ZWL"
    subunit = 100


ZWL: Final = ZWLType()
__currencies.add(ZWL)


@final
class ZWRType(Currency):
    code = "ZWR"
    subunit = 100


ZWR: Final = ZWRType()
__currencies.add(ZWR)


@final
class AOKType(Currency):
    code = "AOK"
    subunit = 1


AOK: Final = AOKType()
__currencies.add(AOK)


@final
class ARLType(Currency):
    code = "ARL"
    subunit = 100


ARL: Final = ARLType()
__currencies.add(ARL)


@final
class ARMType(Currency):
    code = "ARM"
    subunit = 100


ARM: Final = ARMType()
__currencies.add(ARM)


@final
class BANType(Currency):
    code = "BAN"
    subunit = 1


BAN: Final = BANType()
__currencies.add(BAN)


@final
class BECType(Currency):
    code = "BEC"
    subunit = 1


BEC: Final = BECType()
__currencies.add(BEC)


@final
class BELType(Currency):
    code = "BEL"
    subunit = 1


BEL: Final = BELType()
__currencies.add(BEL)


@final
class BGMType(Currency):
    code = "BGM"
    subunit = 1


BGM: Final = BGMType()
__currencies.add(BGM)


@final
class BGOType(Currency):
    code = "BGO"
    subunit = 1


BGO: Final = BGOType()
__currencies.add(BGO)


@final
class BOLType(Currency):
    code = "BOL"
    subunit = 1


BOL: Final = BOLType()
__currencies.add(BOL)


@final
class BOPType(Currency):
    code = "BOP"
    subunit = 100


BOP: Final = BOPType()
__currencies.add(BOP)


@final
class BRBType(Currency):
    code = "BRB"
    subunit = 100


BRB: Final = BRBType()
__currencies.add(BRB)


@final
class BRZType(Currency):
    code = "BRZ"
    subunit = 100


BRZ: Final = BRZType()
__currencies.add(BRZ)


@final
class BUKType(Currency):
    code = "BUK"
    subunit = 1


BUK: Final = BUKType()
__currencies.add(BUK)


@final
class BYBType(Currency):
    code = "BYB"
    subunit = 100


BYB: Final = BYBType()
__currencies.add(BYB)


@final
class CNHType(Currency):
    code = "CNH"
    subunit = 100


CNH: Final = CNHType()
__currencies.add(CNH)


@final
class CNXType(Currency):
    code = "CNX"
    subunit = 100


CNX: Final = CNXType()
__currencies.add(CNX)


@final
class GEKType(Currency):
    code = "GEK"
    subunit = 1


GEK: Final = GEKType()
__currencies.add(GEK)


@final
class GNSType(Currency):
    code = "GNS"
    subunit = 1


GNS: Final = GNSType()
__currencies.add(GNS)


@final
class GQEType(Currency):
    code = "GQE"
    subunit = 1


GQE: Final = GQEType()
__currencies.add(GQE)


@final
class GWEType(Currency):
    code = "GWE"
    subunit = 1


GWE: Final = GWEType()
__currencies.add(GWE)


@final
class ILPType(Currency):
    code = "ILP"
    subunit = 100


ILP: Final = ILPType()
__currencies.add(ILP)


@final
class ILRType(Currency):
    code = "ILR"
    subunit = 100


ILR: Final = ILRType()
__currencies.add(ILR)


@final
class ISJType(Currency):
    code = "ISJ"
    subunit = 100


ISJ: Final = ISJType()
__currencies.add(ISJ)


@final
class KRHType(Currency):
    code = "KRH"
    subunit = 1


KRH: Final = KRHType()
__currencies.add(KRH)


@final
class KROType(Currency):
    code = "KRO"
    subunit = 1


KRO: Final = KROType()
__currencies.add(KRO)


@final
class LTTType(Currency):
    code = "LTT"
    subunit = 100


LTT: Final = LTTType()
__currencies.add(LTT)


@final
class LUCType(Currency):
    code = "LUC"
    subunit = 1


LUC: Final = LUCType()
__currencies.add(LUC)


@final
class LULType(Currency):
    code = "LUL"
    subunit = 1


LUL: Final = LULType()
__currencies.add(LUL)


@final
class LVRType(Currency):
    code = "LVR"
    subunit = 100


LVR: Final = LVRType()
__currencies.add(LVR)


@final
class MAFType(Currency):
    code = "MAF"
    subunit = 100


MAF: Final = MAFType()
__currencies.add(MAF)


@final
class MCFType(Currency):
    code = "MCF"
    subunit = 100


MCF: Final = MCFType()
__currencies.add(MCF)


@final
class MDCType(Currency):
    code = "MDC"
    subunit = 1


MDC: Final = MDCType()
__currencies.add(MDC)


@final
class MKNType(Currency):
    code = "MKN"
    subunit = 1


MKN: Final = MKNType()
__currencies.add(MKN)


@final
class MRUType(Currency):
    code = "MRU"
    subunit = 100


MRU: Final = MRUType()
__currencies.add(MRU)


@final
class MTPType(Currency):
    code = "MTP"
    subunit = 1


MTP: Final = MTPType()
__currencies.add(MTP)


@final
class MVPType(Currency):
    code = "MVP"
    subunit = 1


MVP: Final = MVPType()
__currencies.add(MVP)


@final
class MXPType(Currency):
    code = "MXP"
    subunit = 1


MXP: Final = MXPType()
__currencies.add(MXP)


@final
class MZEType(Currency):
    code = "MZE"
    subunit = 100


MZE: Final = MZEType()
__currencies.add(MZE)


@final
class NICType(Currency):
    code = "NIC"
    subunit = 100


NIC: Final = NICType()
__currencies.add(NIC)


@final
class PESType(Currency):
    code = "PES"
    subunit = 100


PES: Final = PESType()
__currencies.add(PES)


@final
class RHDType(Currency):
    code = "RHD"
    subunit = 100


RHD: Final = RHDType()
__currencies.add(RHD)


@final
class SDPType(Currency):
    code = "SDP"
    subunit = 1


SDP: Final = SDPType()
__currencies.add(SDP)


@final
class STNType(Currency):
    code = "STN"
    subunit = 100


STN: Final = STNType()
__currencies.add(STN)


@final
class SURType(Currency):
    code = "SUR"
    subunit = 1


SUR: Final = SURType()
__currencies.add(SUR)


@final
class UGSType(Currency):
    code = "UGS"
    subunit = 1


UGS: Final = UGSType()
__currencies.add(UGS)


@final
class UYPType(Currency):
    code = "UYP"
    subunit = 100


UYP: Final = UYPType()
__currencies.add(UYP)


@final
class UYWType(Currency):
    code = "UYW"
    subunit = 10000


UYW: Final = UYWType()
__currencies.add(UYW)


@final
class VESType(Currency):
    code = "VES"
    subunit = 100


VES: Final = VESType()
__currencies.add(VES)


@final
class XREType(Currency):
    code = "XRE"
    subunit = 1


XRE: Final = XREType()
__currencies.add(XRE)


@final
class YUDType(Currency):
    code = "YUD"
    subunit = 100


YUD: Final = YUDType()
__currencies.add(YUD)


@final
class YURType(Currency):
    code = "YUR"
    subunit = 100


YUR: Final = YURType()
__currencies.add(YUR)


@final
class AEDType(Currency):
    code = "AED"
    subunit = 100


AED: Final = AEDType()
__currencies.add(AED)


@final
class AFNType(Currency):
    code = "AFN"
    subunit = 100


AFN: Final = AFNType()
__currencies.add(AFN)


@final
class ALLType(Currency):
    code = "ALL"
    subunit = 100


ALL: Final = ALLType()
__currencies.add(ALL)


@final
class AMDType(Currency):
    code = "AMD"
    subunit = 100


AMD: Final = AMDType()
__currencies.add(AMD)


@final
class ANGType(Currency):
    code = "ANG"
    subunit = 100


ANG: Final = ANGType()
__currencies.add(ANG)


@final
class AOAType(Currency):
    code = "AOA"
    subunit = 100


AOA: Final = AOAType()
__currencies.add(AOA)


@final
class ARSType(Currency):
    code = "ARS"
    subunit = 100


ARS: Final = ARSType()
__currencies.add(ARS)


@final
class AUDType(Currency):
    code = "AUD"
    subunit = 100


AUD: Final = AUDType()
__currencies.add(AUD)


@final
class AWGType(Currency):
    code = "AWG"
    subunit = 100


AWG: Final = AWGType()
__currencies.add(AWG)


@final
class AZNType(Currency):
    code = "AZN"
    subunit = 100


AZN: Final = AZNType()
__currencies.add(AZN)


@final
class BAMType(Currency):
    code = "BAM"
    subunit = 100


BAM: Final = BAMType()
__currencies.add(BAM)


@final
class BBDType(Currency):
    code = "BBD"
    subunit = 100


BBD: Final = BBDType()
__currencies.add(BBD)


@final
class BDTType(Currency):
    code = "BDT"
    subunit = 100


BDT: Final = BDTType()
__currencies.add(BDT)


@final
class BGNType(Currency):
    code = "BGN"
    subunit = 100


BGN: Final = BGNType()
__currencies.add(BGN)


@final
class BHDType(Currency):
    code = "BHD"
    subunit = 1000


BHD: Final = BHDType()
__currencies.add(BHD)


@final
class BIFType(Currency):
    code = "BIF"
    subunit = 1


BIF: Final = BIFType()
__currencies.add(BIF)


@final
class BMDType(Currency):
    code = "BMD"
    subunit = 100


BMD: Final = BMDType()
__currencies.add(BMD)


@final
class BNDType(Currency):
    code = "BND"
    subunit = 100


BND: Final = BNDType()
__currencies.add(BND)


@final
class BOBType(Currency):
    code = "BOB"
    subunit = 100


BOB: Final = BOBType()
__currencies.add(BOB)


@final
class BOVType(Currency):
    code = "BOV"
    subunit = 100


BOV: Final = BOVType()
__currencies.add(BOV)


@final
class BRLType(Currency):
    code = "BRL"
    subunit = 100


BRL: Final = BRLType()
__currencies.add(BRL)


@final
class BSDType(Currency):
    code = "BSD"
    subunit = 100


BSD: Final = BSDType()
__currencies.add(BSD)


@final
class BTNType(Currency):
    code = "BTN"
    subunit = 100


BTN: Final = BTNType()
__currencies.add(BTN)


@final
class BWPType(Currency):
    code = "BWP"
    subunit = 100


BWP: Final = BWPType()
__currencies.add(BWP)


@final
class BYNType(Currency):
    code = "BYN"
    subunit = 100


BYN: Final = BYNType()
__currencies.add(BYN)


@final
class BZDType(Currency):
    code = "BZD"
    subunit = 100


BZD: Final = BZDType()
__currencies.add(BZD)


@final
class CADType(Currency):
    code = "CAD"
    subunit = 100


CAD: Final = CADType()
__currencies.add(CAD)


@final
class CDFType(Currency):
    code = "CDF"
    subunit = 100


CDF: Final = CDFType()
__currencies.add(CDF)


@final
class CHEType(Currency):
    code = "CHE"
    subunit = 100


CHE: Final = CHEType()
__currencies.add(CHE)


@final
class CHFType(Currency):
    code = "CHF"
    subunit = 100


CHF: Final = CHFType()
__currencies.add(CHF)


@final
class CHWType(Currency):
    code = "CHW"
    subunit = 100


CHW: Final = CHWType()
__currencies.add(CHW)


@final
class CLFType(Currency):
    code = "CLF"
    subunit = 10000


CLF: Final = CLFType()
__currencies.add(CLF)


@final
class CLPType(Currency):
    code = "CLP"
    subunit = 1


CLP: Final = CLPType()
__currencies.add(CLP)


@final
class CNYType(Currency):
    code = "CNY"
    subunit = 100


CNY: Final = CNYType()
__currencies.add(CNY)


@final
class COPType(Currency):
    code = "COP"
    subunit = 100


COP: Final = COPType()
__currencies.add(COP)


@final
class COUType(Currency):
    code = "COU"
    subunit = 100


COU: Final = COUType()
__currencies.add(COU)


@final
class CRCType(Currency):
    code = "CRC"
    subunit = 100


CRC: Final = CRCType()
__currencies.add(CRC)


@final
class CUCType(Currency):
    code = "CUC"
    subunit = 100


CUC: Final = CUCType()
__currencies.add(CUC)


@final
class CUPType(Currency):
    code = "CUP"
    subunit = 100


CUP: Final = CUPType()
__currencies.add(CUP)


@final
class CVEType(Currency):
    code = "CVE"
    subunit = 100


CVE: Final = CVEType()
__currencies.add(CVE)


@final
class CZKType(Currency):
    code = "CZK"
    subunit = 100


CZK: Final = CZKType()
__currencies.add(CZK)


@final
class DJFType(Currency):
    code = "DJF"
    subunit = 1


DJF: Final = DJFType()
__currencies.add(DJF)


@final
class DKKType(Currency):
    code = "DKK"
    subunit = 100


DKK: Final = DKKType()
__currencies.add(DKK)


@final
class DOPType(Currency):
    code = "DOP"
    subunit = 100


DOP: Final = DOPType()
__currencies.add(DOP)


@final
class DZDType(Currency):
    code = "DZD"
    subunit = 100


DZD: Final = DZDType()
__currencies.add(DZD)


@final
class EGPType(Currency):
    code = "EGP"
    subunit = 100


EGP: Final = EGPType()
__currencies.add(EGP)


@final
class ERNType(Currency):
    code = "ERN"
    subunit = 100


ERN: Final = ERNType()
__currencies.add(ERN)


@final
class ETBType(Currency):
    code = "ETB"
    subunit = 100


ETB: Final = ETBType()
__currencies.add(ETB)


@final
class EURType(Currency):
    code = "EUR"
    subunit = 100


EUR: Final = EURType()
__currencies.add(EUR)


@final
class FJDType(Currency):
    code = "FJD"
    subunit = 100


FJD: Final = FJDType()
__currencies.add(FJD)


@final
class FKPType(Currency):
    code = "FKP"
    subunit = 100


FKP: Final = FKPType()
__currencies.add(FKP)


@final
class GBPType(Currency):
    code = "GBP"
    subunit = 100


GBP: Final = GBPType()
__currencies.add(GBP)


@final
class GELType(Currency):
    code = "GEL"
    subunit = 100


GEL: Final = GELType()
__currencies.add(GEL)


@final
class GHSType(Currency):
    code = "GHS"
    subunit = 100


GHS: Final = GHSType()
__currencies.add(GHS)


@final
class GIPType(Currency):
    code = "GIP"
    subunit = 100


GIP: Final = GIPType()
__currencies.add(GIP)


@final
class GMDType(Currency):
    code = "GMD"
    subunit = 100


GMD: Final = GMDType()
__currencies.add(GMD)


@final
class GNFType(Currency):
    code = "GNF"
    subunit = 1


GNF: Final = GNFType()
__currencies.add(GNF)


@final
class GTQType(Currency):
    code = "GTQ"
    subunit = 100


GTQ: Final = GTQType()
__currencies.add(GTQ)


@final
class GYDType(Currency):
    code = "GYD"
    subunit = 100


GYD: Final = GYDType()
__currencies.add(GYD)


@final
class HKDType(Currency):
    code = "HKD"
    subunit = 100


HKD: Final = HKDType()
__currencies.add(HKD)


@final
class HNLType(Currency):
    code = "HNL"
    subunit = 100


HNL: Final = HNLType()
__currencies.add(HNL)


@final
class HRKType(Currency):
    code = "HRK"
    subunit = 100


HRK: Final = HRKType()
__currencies.add(HRK)


@final
class HTGType(Currency):
    code = "HTG"
    subunit = 100


HTG: Final = HTGType()
__currencies.add(HTG)


@final
class HUFType(Currency):
    code = "HUF"
    subunit = 100


HUF: Final = HUFType()
__currencies.add(HUF)


@final
class IDRType(Currency):
    code = "IDR"
    subunit = 100


IDR: Final = IDRType()
__currencies.add(IDR)


@final
class ILSType(Currency):
    code = "ILS"
    subunit = 100


ILS: Final = ILSType()
__currencies.add(ILS)


@final
class IMPType(Currency):
    code = "IMP"
    subunit = 100


IMP: Final = IMPType()
__currencies.add(IMP)


@final
class INRType(Currency):
    code = "INR"
    subunit = 100


INR: Final = INRType()
__currencies.add(INR)


@final
class IQDType(Currency):
    code = "IQD"
    subunit = 1000


IQD: Final = IQDType()
__currencies.add(IQD)


@final
class IRRType(Currency):
    code = "IRR"
    subunit = 100


IRR: Final = IRRType()
__currencies.add(IRR)


@final
class ISKType(Currency):
    code = "ISK"
    subunit = 1


ISK: Final = ISKType()
__currencies.add(ISK)


@final
class JMDType(Currency):
    code = "JMD"
    subunit = 100


JMD: Final = JMDType()
__currencies.add(JMD)


@final
class JODType(Currency):
    code = "JOD"
    subunit = 1000


JOD: Final = JODType()
__currencies.add(JOD)


@final
class JPYType(Currency):
    code = "JPY"
    subunit = 1


JPY: Final = JPYType()
__currencies.add(JPY)


@final
class KESType(Currency):
    code = "KES"
    subunit = 100


KES: Final = KESType()
__currencies.add(KES)


@final
class KGSType(Currency):
    code = "KGS"
    subunit = 100


KGS: Final = KGSType()
__currencies.add(KGS)


@final
class KHRType(Currency):
    code = "KHR"
    subunit = 100


KHR: Final = KHRType()
__currencies.add(KHR)


@final
class KMFType(Currency):
    code = "KMF"
    subunit = 1


KMF: Final = KMFType()
__currencies.add(KMF)


@final
class KPWType(Currency):
    code = "KPW"
    subunit = 100


KPW: Final = KPWType()
__currencies.add(KPW)


@final
class KRWType(Currency):
    code = "KRW"
    subunit = 1


KRW: Final = KRWType()
__currencies.add(KRW)


@final
class KWDType(Currency):
    code = "KWD"
    subunit = 1000


KWD: Final = KWDType()
__currencies.add(KWD)


@final
class KYDType(Currency):
    code = "KYD"
    subunit = 100


KYD: Final = KYDType()
__currencies.add(KYD)


@final
class KZTType(Currency):
    code = "KZT"
    subunit = 100


KZT: Final = KZTType()
__currencies.add(KZT)


@final
class LAKType(Currency):
    code = "LAK"
    subunit = 100


LAK: Final = LAKType()
__currencies.add(LAK)


@final
class LBPType(Currency):
    code = "LBP"
    subunit = 100


LBP: Final = LBPType()
__currencies.add(LBP)


@final
class LKRType(Currency):
    code = "LKR"
    subunit = 100


LKR: Final = LKRType()
__currencies.add(LKR)


@final
class LRDType(Currency):
    code = "LRD"
    subunit = 100


LRD: Final = LRDType()
__currencies.add(LRD)


@final
class LSLType(Currency):
    code = "LSL"
    subunit = 100


LSL: Final = LSLType()
__currencies.add(LSL)


@final
class LYDType(Currency):
    code = "LYD"
    subunit = 1000


LYD: Final = LYDType()
__currencies.add(LYD)


@final
class MADType(Currency):
    code = "MAD"
    subunit = 100


MAD: Final = MADType()
__currencies.add(MAD)


@final
class MDLType(Currency):
    code = "MDL"
    subunit = 100


MDL: Final = MDLType()
__currencies.add(MDL)


@final
class MGAType(Currency):
    code = "MGA"
    subunit = 100


MGA: Final = MGAType()
__currencies.add(MGA)


@final
class MKDType(Currency):
    code = "MKD"
    subunit = 100


MKD: Final = MKDType()
__currencies.add(MKD)


@final
class MMKType(Currency):
    code = "MMK"
    subunit = 100


MMK: Final = MMKType()
__currencies.add(MMK)


@final
class MNTType(Currency):
    code = "MNT"
    subunit = 100


MNT: Final = MNTType()
__currencies.add(MNT)


@final
class MOPType(Currency):
    code = "MOP"
    subunit = 100


MOP: Final = MOPType()
__currencies.add(MOP)


@final
class MURType(Currency):
    code = "MUR"
    subunit = 100


MUR: Final = MURType()
__currencies.add(MUR)


@final
class MVRType(Currency):
    code = "MVR"
    subunit = 100


MVR: Final = MVRType()
__currencies.add(MVR)


@final
class MWKType(Currency):
    code = "MWK"
    subunit = 100


MWK: Final = MWKType()
__currencies.add(MWK)


@final
class MXNType(Currency):
    code = "MXN"
    subunit = 100


MXN: Final = MXNType()
__currencies.add(MXN)


@final
class MXVType(Currency):
    code = "MXV"
    subunit = 100


MXV: Final = MXVType()
__currencies.add(MXV)


@final
class MYRType(Currency):
    code = "MYR"
    subunit = 100


MYR: Final = MYRType()
__currencies.add(MYR)


@final
class MZNType(Currency):
    code = "MZN"
    subunit = 100


MZN: Final = MZNType()
__currencies.add(MZN)


@final
class NADType(Currency):
    code = "NAD"
    subunit = 100


NAD: Final = NADType()
__currencies.add(NAD)


@final
class NGNType(Currency):
    code = "NGN"
    subunit = 100


NGN: Final = NGNType()
__currencies.add(NGN)


@final
class NIOType(Currency):
    code = "NIO"
    subunit = 100


NIO: Final = NIOType()
__currencies.add(NIO)


@final
class NOKType(Currency):
    code = "NOK"
    subunit = 100


NOK: Final = NOKType()
__currencies.add(NOK)


@final
class NPRType(Currency):
    code = "NPR"
    subunit = 100


NPR: Final = NPRType()
__currencies.add(NPR)


@final
class NZDType(Currency):
    code = "NZD"
    subunit = 100


NZD: Final = NZDType()
__currencies.add(NZD)


@final
class OMRType(Currency):
    code = "OMR"
    subunit = 1000


OMR: Final = OMRType()
__currencies.add(OMR)


@final
class PABType(Currency):
    code = "PAB"
    subunit = 100


PAB: Final = PABType()
__currencies.add(PAB)


@final
class PENType(Currency):
    code = "PEN"
    subunit = 100


PEN: Final = PENType()
__currencies.add(PEN)


@final
class PGKType(Currency):
    code = "PGK"
    subunit = 100


PGK: Final = PGKType()
__currencies.add(PGK)


@final
class PHPType(Currency):
    code = "PHP"
    subunit = 100


PHP: Final = PHPType()
__currencies.add(PHP)


@final
class PKRType(Currency):
    code = "PKR"
    subunit = 100


PKR: Final = PKRType()
__currencies.add(PKR)


@final
class PLNType(Currency):
    code = "PLN"
    subunit = 100


PLN: Final = PLNType()
__currencies.add(PLN)


@final
class PYGType(Currency):
    code = "PYG"
    subunit = 1


PYG: Final = PYGType()
__currencies.add(PYG)


@final
class QARType(Currency):
    code = "QAR"
    subunit = 100


QAR: Final = QARType()
__currencies.add(QAR)


@final
class RONType(Currency):
    code = "RON"
    subunit = 100


RON: Final = RONType()
__currencies.add(RON)


@final
class RSDType(Currency):
    code = "RSD"
    subunit = 100


RSD: Final = RSDType()
__currencies.add(RSD)


@final
class RUBType(Currency):
    code = "RUB"
    subunit = 100


RUB: Final = RUBType()
__currencies.add(RUB)


@final
class RWFType(Currency):
    code = "RWF"
    subunit = 1


RWF: Final = RWFType()
__currencies.add(RWF)


@final
class SARType(Currency):
    code = "SAR"
    subunit = 100


SAR: Final = SARType()
__currencies.add(SAR)


@final
class SBDType(Currency):
    code = "SBD"
    subunit = 100


SBD: Final = SBDType()
__currencies.add(SBD)


@final
class SCRType(Currency):
    code = "SCR"
    subunit = 100


SCR: Final = SCRType()
__currencies.add(SCR)


@final
class SDGType(Currency):
    code = "SDG"
    subunit = 100


SDG: Final = SDGType()
__currencies.add(SDG)


@final
class SEKType(Currency):
    code = "SEK"
    subunit = 100


SEK: Final = SEKType()
__currencies.add(SEK)


@final
class SGDType(Currency):
    code = "SGD"
    subunit = 100


SGD: Final = SGDType()
__currencies.add(SGD)


@final
class SHPType(Currency):
    code = "SHP"
    subunit = 100


SHP: Final = SHPType()
__currencies.add(SHP)


@final
class SLEType(Currency):
    code = "SLE"
    subunit = 100


SLE: Final = SLEType()
__currencies.add(SLE)


@final
class SLLType(Currency):
    code = "SLL"
    subunit = 100


SLL: Final = SLLType()
__currencies.add(SLL)


@final
class SOSType(Currency):
    code = "SOS"
    subunit = 100


SOS: Final = SOSType()
__currencies.add(SOS)


@final
class SRDType(Currency):
    code = "SRD"
    subunit = 100


SRD: Final = SRDType()
__currencies.add(SRD)


@final
class SSPType(Currency):
    code = "SSP"
    subunit = 100


SSP: Final = SSPType()
__currencies.add(SSP)


@final
class SVCType(Currency):
    code = "SVC"
    subunit = 100


SVC: Final = SVCType()
__currencies.add(SVC)


@final
class SYPType(Currency):
    code = "SYP"
    subunit = 100


SYP: Final = SYPType()
__currencies.add(SYP)


@final
class SZLType(Currency):
    code = "SZL"
    subunit = 100


SZL: Final = SZLType()
__currencies.add(SZL)


@final
class THBType(Currency):
    code = "THB"
    subunit = 100


THB: Final = THBType()
__currencies.add(THB)


@final
class TJSType(Currency):
    code = "TJS"
    subunit = 100


TJS: Final = TJSType()
__currencies.add(TJS)


@final
class TMTType(Currency):
    code = "TMT"
    subunit = 100


TMT: Final = TMTType()
__currencies.add(TMT)


@final
class TNDType(Currency):
    code = "TND"
    subunit = 1000


TND: Final = TNDType()
__currencies.add(TND)


@final
class TOPType(Currency):
    code = "TOP"
    subunit = 100


TOP: Final = TOPType()
__currencies.add(TOP)


@final
class TRYType(Currency):
    code = "TRY"
    subunit = 100


TRY: Final = TRYType()
__currencies.add(TRY)


@final
class TTDType(Currency):
    code = "TTD"
    subunit = 100


TTD: Final = TTDType()
__currencies.add(TTD)


@final
class TVDType(Currency):
    code = "TVD"
    subunit = 100


TVD: Final = TVDType()
__currencies.add(TVD)


@final
class TWDType(Currency):
    code = "TWD"
    subunit = 100


TWD: Final = TWDType()
__currencies.add(TWD)


@final
class TZSType(Currency):
    code = "TZS"
    subunit = 100


TZS: Final = TZSType()
__currencies.add(TZS)


@final
class UAHType(Currency):
    code = "UAH"
    subunit = 100


UAH: Final = UAHType()
__currencies.add(UAH)


@final
class UGXType(Currency):
    code = "UGX"
    subunit = 1


UGX: Final = UGXType()
__currencies.add(UGX)


@final
class USDType(Currency):
    code = "USD"
    subunit = 100


USD: Final = USDType()
__currencies.add(USD)


@final
class USNType(Currency):
    code = "USN"
    subunit = 100


USN: Final = USNType()
__currencies.add(USN)


@final
class UYIType(Currency):
    code = "UYI"
    subunit = 1


UYI: Final = UYIType()
__currencies.add(UYI)


@final
class UYUType(Currency):
    code = "UYU"
    subunit = 100


UYU: Final = UYUType()
__currencies.add(UYU)


@final
class UZSType(Currency):
    code = "UZS"
    subunit = 100


UZS: Final = UZSType()
__currencies.add(UZS)


@final
class VEDType(Currency):
    code = "VED"
    subunit = 100


VED: Final = VEDType()
__currencies.add(VED)


@final
class VNDType(Currency):
    code = "VND"
    subunit = 1


VND: Final = VNDType()
__currencies.add(VND)


@final
class VUVType(Currency):
    code = "VUV"
    subunit = 1


VUV: Final = VUVType()
__currencies.add(VUV)


@final
class WSTType(Currency):
    code = "WST"
    subunit = 100


WST: Final = WSTType()
__currencies.add(WST)


@final
class XAFType(Currency):
    code = "XAF"
    subunit = 1


XAF: Final = XAFType()
__currencies.add(XAF)


@final
class XAGType(Currency):
    code = "XAG"
    subunit = 1


XAG: Final = XAGType()
__currencies.add(XAG)


@final
class XAUType(Currency):
    code = "XAU"
    subunit = 1


XAU: Final = XAUType()
__currencies.add(XAU)


@final
class XBAType(Currency):
    code = "XBA"
    subunit = 1


XBA: Final = XBAType()
__currencies.add(XBA)


@final
class XBBType(Currency):
    code = "XBB"
    subunit = 1


XBB: Final = XBBType()
__currencies.add(XBB)


@final
class XBCType(Currency):
    code = "XBC"
    subunit = 1


XBC: Final = XBCType()
__currencies.add(XBC)


@final
class XBDType(Currency):
    code = "XBD"
    subunit = 1


XBD: Final = XBDType()
__currencies.add(XBD)


@final
class XCDType(Currency):
    code = "XCD"
    subunit = 100


XCD: Final = XCDType()
__currencies.add(XCD)


@final
class XDRType(Currency):
    code = "XDR"
    subunit = 1


XDR: Final = XDRType()
__currencies.add(XDR)


@final
class XFOType(Currency):
    code = "XFO"
    subunit = 1


XFO: Final = XFOType()
__currencies.add(XFO)


@final
class XFUType(Currency):
    code = "XFU"
    subunit = 1


XFU: Final = XFUType()
__currencies.add(XFU)


@final
class XOFType(Currency):
    code = "XOF"
    subunit = 1


XOF: Final = XOFType()
__currencies.add(XOF)


@final
class XPDType(Currency):
    code = "XPD"
    subunit = 1


XPD: Final = XPDType()
__currencies.add(XPD)


@final
class XPFType(Currency):
    code = "XPF"
    subunit = 1


XPF: Final = XPFType()
__currencies.add(XPF)


@final
class XPTType(Currency):
    code = "XPT"
    subunit = 1


XPT: Final = XPTType()
__currencies.add(XPT)


@final
class XSUType(Currency):
    code = "XSU"
    subunit = 1


XSU: Final = XSUType()
__currencies.add(XSU)


@final
class XTSType(Currency):
    code = "XTS"
    subunit = 1


XTS: Final = XTSType()
__currencies.add(XTS)


@final
class XUAType(Currency):
    code = "XUA"
    subunit = 1


XUA: Final = XUAType()
__currencies.add(XUA)


@final
class XXXType(Currency):
    code = "XXX"
    subunit = 1


XXX: Final = XXXType()
__currencies.add(XXX)


@final
class YERType(Currency):
    code = "YER"
    subunit = 100


YER: Final = YERType()
__currencies.add(YER)


@final
class ZARType(Currency):
    code = "ZAR"
    subunit = 100


ZAR: Final = ZARType()
__currencies.add(ZAR)


@final
class ZMWType(Currency):
    code = "ZMW"
    subunit = 100


ZMW: Final = ZMWType()
__currencies.add(ZMW)


@final
class ZWNType(Currency):
    code = "ZWN"
    subunit = 100


ZWN: Final = ZWNType()
__currencies.add(ZWN)


registry: Final[CurrencyRegistry[Currency]] = __currencies.finalize()
del __currencies
