# Description: BBCW installation parameters for LHC Run III

# Default locations, _bbcw_name   = f'bbcw.{tank}.{loc}.{beam_name}'
# ----------------------------
beam_list = ['b1', 'b2']
loc_list  = {   'b1':['4l1','4l5'],
                'b2':['4r1','4r5']}
tank_list = ['a', 'b']


# Location B1
# -----------------------------------------
bbcw_insert = {}
bbcw_insert['b1'] = {   # IP1 =========================================
                        'bbcw.a.4l1.b1':{'at_s':0 , 'from':'tctpv.4l1.b1'},
                        'bbcw.b.4l1.b1':{'at_s':0 , 'from':'tctpv.4l1.b1'},
                        # IP5 =========================================
                        'bbcw.a.4l5.b1':{'at_s':0 , 'from':'tctph.4l5.b1'},
                        'bbcw.b.4l5.b1':{'at_s':0 , 'from':'tctph.4l5.b1'}}


bbcw_insert['b2'] = {   # IP1 =========================================
                        'bbcw.a.4r1.b2':{'at_s':0 , 'from':'tctpv.4r1.b2'},
                        'bbcw.b.4r1.b2':{'at_s':0 , 'from':'tctpv.4r1.b2'},
                        # IP5 =========================================
                        'bbcw.a.4r5.b2':{'at_s':0 , 'from':'tctph.4r5.b2'},
                        'bbcw.b.4r5.b2':{'at_s':0 , 'from':'tctph.4r5.b2'}}


# Orientation (LHC, V3.0)
# -----------------------------------------
bbcw_orientation_xy = lambda _name: {   # Beam 1
                                        ('a', '4l1') :(  0,  1), # ip1, vertical, top
                                        ('b', '4l1') :(  0, -1), # ip1, vertical, bot
                                        ('a', '4l5') :(  1,  0), # ip5, horizontal, ext.
                                        ('b', '4l5') :( -1,  0), # ip5, horizontal, int.
                                        # Beam 2
                                        ('a', '4r1') :(  0,  1), # ip1, vertical, top
                                        ('b', '4r1') :(  0, -1), # ip1, vertical, bot
                                        ('a', '4r5') :(  1,  0), # ip5, horizontal, ext.
                                        ('b', '4r5') :( -1,  0), # ip5, horizontal, int.
                                        }[tuple(_name.split('.')[1:3])]



collimation_emittance = {   'x' : 3.5e-6, 
                            'y' : 3.5e-6}

# ==================================================================================================
# --- BBCW Matching knobs (see knobify_kq_bbcw function)
# ==================================================================================================
# from /afs/cern.ch/eng/lhc/optics/runIII/LHC_LS2_2021-07-02.seq
kq_vary_dict = {    'kq4'       : {'include':True, 'limits':['kmin_mqy_4.5k','kmax_mqy_4.5k']    ,'step':1e-8,'rel_lim':0.1},
                    'kq5'       : {'include':True, 'limits':['kmin_mqml_4.5k','kmax_mqml_4.5k']  ,'step':1e-8,'rel_lim':0.1},
                    'kq6'       : {'include':True, 'limits':['kmin_mqml_4.5k','kmax_mqml_4.5k']  ,'step':1e-8,'rel_lim':0.1},
                    'kq7'       : {'include':True, 'limits':['kmin_mqm','kmax_mqm']              ,'step':1e-8,'rel_lim':0.1},
                    'kq8'       : {'include':True, 'limits':['kmin_mqml','kmax_mqml']            ,'step':1e-8,'rel_lim':0.1},
                    'kq9'       : {'include':True, 'limits':['kmin_mqmc','kmax_mqmc']            ,'step':1e-8,'rel_lim':0.1},
                    'kq10'      : {'include':True, 'limits':['kmin_mqml','kmax_mqml']            ,'step':1e-8,'rel_lim':0.1},
                    'kqtl11'    : {'include':True, 'limits':['kmin_mqtli','kmax_mqtli']          ,'step':1e-8,'rel_lim':0.1},
                    'kqt12'     : {'include':True, 'limits':['kmin_mqt','kmax_mqt']              ,'step':1e-8,'rel_lim':0.1},
                    'kqt13'     : {'include':True, 'limits':['kmin_mqt','kmax_mqt']              ,'step':1e-8,'rel_lim':0.1},}


