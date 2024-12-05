# ==================================================================================================
# --- Imports
# ==================================================================================================
import numpy as np
import xtrack as xt
import scipy.constants

c_light = scipy.constants.speed_of_light  # m s-1
mu0     = scipy.constants.mu_0



# ==================================================================================================
# --- BBCW parameter definition
# ==================================================================================================
# Creating dummy wire element as a template
# -----------------------------------------
master_bbcw = xt.Wire(  L_phy   = 1, 
                        L_int   = 10,
                        current = 0.0,
                        xma     = 1.0, 
                        yma     = 1.0)
master_bbcw.behaves_like_drift  = True
master_bbcw.allow_track         = False



# ==================================================================================================
# --- Function to install BBCW
# ==================================================================================================
def load_version_specific(ver_lhc_run = None,ver_hllhc_optics = None):
    # Get the appropriate installation
    assert (ver_lhc_run is not None and ver_hllhc_optics is None) or (ver_lhc_run is None and  ver_hllhc_optics is not None), "Only one version of the optics can be installed"
    if ver_hllhc_optics is not None:
        match ver_hllhc_optics:
            case 1.6:
                from ..version_specific_files.hllhc16.bbcw_installation import beam_list, loc_list, tank_list, bbcw_insert, bbcw_orientation_xy, collimation_emittance, kq_vary_dict
            case 1.3:
                logging.warning(f"bbcw for HLLHC optics version {ver_hllhc_optics} not implemented yet. Using HLLHC16 optics.")
                from ..version_specific_files.hllhc16.bbcw_installation import beam_list, loc_list, tank_list, bbcw_insert, bbcw_orientation_xy, collimation_emittance, kq_vary_dict
            case _:
                logging.warning(f"bbcw for HLLHC optics version {ver_hllhc_optics} not implemented yet. Using HLLHC16 optics.")
                from ..version_specific_files.hllhc16.bbcw_installation import beam_list, loc_list,  tank_list, bbcw_insert, bbcw_orientation_xy, collimation_emittance, kq_vary_dict

    elif ver_lhc_run is not None:
        match ver_lhc_run:
            case 3.0:
                from ..version_specific_files.runIII.bbcw_installation import beam_list, loc_list, tank_list, bbcw_insert, bbcw_orientation_xy, collimation_emittance, kq_vary_dict
    else:
        raise ValueError("No optics specific tools for the provided configuration")

    return beam_list, loc_list,  tank_list, bbcw_insert, bbcw_orientation_xy, collimation_emittance, kq_vary_dict


class BBCWInstaller:
    """
    BBCWInstaller is responsible for installing and configuring Beam-Beam Compensation Wires (BBCW)
    in a collider environment. It manages the appropriate wire settings and their integration
    into the collider for effective beam compensation.

    Attributes:
        ver_hllhc_optics (float | None): Version of HL-LHC optics to be used. 
        ver_lhc_run (float | None): Version of LHC run to be used.
        beam_list (list): List of beams used in the collider.
        loc_list (dict): Dictionary specifying locations of the BBCW for each beam.
        tank_list (list): List of tank configurations for BBCW.
        bbcw_insert (dict): Instructions for inserting BBCW elements.
        bbcw_orientation_xy (function): Function to determine BBCW orientation.
        collimation_emittance (dict): Emittance values for collimation.
        kq_vary_dict (dict): Dictionary specifying quadrupole variation for BBCW.

    Methods:
        install_bbcw(collider) -> None:
            Installs BBCW elements in the specified collider based on the configuration.
        knobify_kq_bbcw(collider, nominal_current, nominal_distance, parking_current, parking_distance, kq_to_vary) -> dict:
            Creates knobs for the quadrupoles to scale with BBCW effects and performs matching.
        add_normalized_distance_knobs(collider) -> None:
            Adds knobs for normalized wire distances based on beam parameters.
        update_optics_bbcw(collider) -> None:
            Updates closed orbit and optics parameters at BBCW positions.
    """
    def __init__(self,
        ver_hllhc_optics: float |  None = None,
        ver_lhc_run: float |  None = None,
    ):
        """
        Initializes the BBCWInstaller class with the given configuration.

        Args:
            ver_hllhc_optics (float | None): Version of HL-LHC optics to be used.
            ver_lhc_run (float | None): Version of LHC run to be used.
        """

        self.ver_hllhc_optics = ver_hllhc_optics
        self.ver_lhc_run = ver_lhc_run

        # Get the appropriate installation
        _version_specific_installation = load_version_specific(ver_lhc_run, ver_hllhc_optics)
        self.beam_list = _version_specific_installation[0]
        self.loc_list = _version_specific_installation[1]
        self.tank_list = _version_specific_installation[2]
        self.bbcw_insert = _version_specific_installation[3]
        self.bbcw_orientation_xy = _version_specific_installation[4]
        self.collimation_emittance = _version_specific_installation[5]
        self.kq_vary_dict = _version_specific_installation[6]



    def install_bbcw(self,collider):
        """
        Installs the BBCW elements in the collider based on the configuration.

        Args:
            collider: The collider object where BBCW elements are to be installed.

        Returns:
            None
        """
        # Get the appropriate installation
        beam_list = self.beam_list
        loc_list = self.loc_list
        tank_list = self.tank_list
        bbcw_insert = self.bbcw_insert
        bbcw_orientation_xy = self.bbcw_orientation_xy
        collimation_emittance = self.collimation_emittance
        kq_vary_dict = self.kq_vary_dict
        

        # Creating some default knobs:
        # ----------------------------
        for beam_name in beam_list:
            for loc in loc_list[beam_name]:
                # Per tank knobs
                for tank in tank_list:
                    collider.vars[f'i_wire.{tank}.{loc}.{beam_name}']      = 0 
                    collider.vars[f'd_wire.{tank}.{loc}.{beam_name}']      = 1
                    collider.vars[f'co_x_wire.{tank}.{loc}.{beam_name}']   = 0
                    collider.vars[f'co_y_wire.{tank}.{loc}.{beam_name}']   = 0
                    collider.vars[f'sigx_wire.{tank}.{loc}.{beam_name}']   = 1  # To avoid distance @ 0
                    collider.vars[f'sigy_wire.{tank}.{loc}.{beam_name}']   = 1  # To avoid distance @ 0 
                    

        # Boolean knobs to deactivate ff knobs
        # ----------------------------
        collider.vars[f'bbcw_enable_ff_tune']   = 1
        collider.vars[f'bbcw_enable_ff_co']     = 1


        # Installing bbcw elements
        # -------------------------
        for beam_name in beam_list:
            
            # Twiss for location
            _line   = collider[f'lhc{beam_name}']
            _twiss  = _line.twiss4d()
            _line.discard_tracker()

            for loc in loc_list[beam_name]:
                for tank in tank_list:
                    # Finding name
                    _bbcw_name   = f'bbcw.{tank}.{loc}.{beam_name}'
                    _bbcw_insert = bbcw_insert[beam_name][_bbcw_name]
                
                    # Finding s position to insert
                    _at_s  = _bbcw_insert['at_s'] + _twiss.rows[_bbcw_insert['from']].s[0]

                    # Inserting template element
                    _line.insert_element(   name    = _bbcw_name,
                                            at_s    = _at_s,
                                            element = master_bbcw.copy())
                    


                    # Linking "per tank" knobs
                    _line.element_refs[_bbcw_name].current  = collider.vars[f'i_wire.{tank}.{loc}.{beam_name}']
                    _line.element_refs[_bbcw_name].xma      = bbcw_orientation_xy(_bbcw_name)[0]*collider.vars[f'd_wire.{tank}.{loc}.{beam_name}'] + collider.vars[f'co_x_wire.{tank}.{loc}.{beam_name}']
                    _line.element_refs[_bbcw_name].yma      = bbcw_orientation_xy(_bbcw_name)[1]*collider.vars[f'd_wire.{tank}.{loc}.{beam_name}'] + collider.vars[f'co_y_wire.{tank}.{loc}.{beam_name}']
                

                    # Computing dipolar and quadrupolar kick
                    q0      = _line.particle_ref.q0
                    p0      = _line.particle_ref.p0c[0]/c_light
                    const   = -mu0*(q0/p0)/(2*np.pi)
                    IL_eq   = _line.element_refs[_bbcw_name].current._expr * _line.element_refs[_bbcw_name].L_phy._value
                    dx      = _line.element_refs[_bbcw_name].xma._expr
                    dy      = _line.element_refs[_bbcw_name].yma._expr
                    collider.vars[f'knl_0_wire.{tank}.{loc}.{beam_name}'] =  np.real(const*IL_eq/(dx + 1j*dy)**1) # real part
                    collider.vars[f'ksl_0_wire.{tank}.{loc}.{beam_name}'] =  np.imag(const*IL_eq/(dx + 1j*dy)**1) # imag part
                    collider.vars[f'knl_1_wire.{tank}.{loc}.{beam_name}'] =  np.real(const*IL_eq/(dx + 1j*dy)**2) # real part 
                    collider.vars[f'ksl_1_wire.{tank}.{loc}.{beam_name}'] =  np.imag(const*IL_eq/(dx + 1j*dy)**2) # imag part
                    
                    _line.element_refs[_bbcw_name].post_subtract_px = -collider.vars[f'knl_0_wire.{tank}.{loc}.{beam_name}']*collider.vars[f'bbcw_enable_ff_co'] # dpx \propto -knl
                    _line.element_refs[_bbcw_name].post_subtract_py =  collider.vars[f'ksl_0_wire.{tank}.{loc}.{beam_name}']*collider.vars[f'bbcw_enable_ff_co'] # dpy \propto +ksl


        # updating closed orbit and beta @ wires
        # -------------------------
        self.update_optics_bbcw(collider)



    # ==================================================================================================
    # --- BBCW Knobify function
    # ==================================================================================================
    def knobify_kq_bbcw(self,collider,config_nominal = None,nominal_current=150,nominal_distance=10e-3,kq_to_vary = None):
        """
        Creates knobs for quadrupoles to scale with BBCW effects and performs matching.

        Args:
            collider: The collider object to configure.
            config_nominal (dict | None): Nominal configuration for the wires, supercedes nominal_current and nominal_distance)
            nominal_current (float): Nominal current for the wires.
            nominal_distance (float): Nominal distance of the wires.
            kq_to_vary (list | None): List of quadrupoles to vary.

        Returns:
            dict: Matching configurations for each location.
        """
        # Get the appropriate installation
        beam_list = self.beam_list
        loc_list = self.loc_list
        tank_list = self.tank_list
        bbcw_insert = self.bbcw_insert
        bbcw_orientation_xy = self.bbcw_orientation_xy
        collimation_emittance = self.collimation_emittance
        kq_vary_dict = self.kq_vary_dict

        # Get the value from config
        parking_current =0
        parking_distance=1
        if config_nominal is not None:
            nominal_current = config_nominal['nominal_current']
            nominal_distance= config_nominal['nominal_distance']
            kq_to_vary      = config_nominal['kq_to_vary']



        # Updating kq_vary_dict
        # ----------------------------
        if kq_to_vary is not None:
            for kq in kq_vary_dict.keys():
                if kq not in kq_to_vary:
                    kq_vary_dict[kq]['include'] = False
                else:
                    kq_vary_dict[kq]['include'] = True


        

        # Knobifying the quadrupoles
        #---------------------------------------------
        for beam_name in beam_list:
            for loc in loc_list[beam_name]:

                # Creating knobs for the matching:
                for kq in kq_vary_dict.keys():
                    # Skipping if not included
                    if kq_vary_dict[kq]['include'] == False: continue
                    
                    # Saving reference value
                    kq_knob = f'{kq}.{loc[1:]}{beam_name}' # e.g. kq4.l1b1
                    collider.vars[f'{kq_knob}_ref'] = collider.vars[f'{kq_knob}']._value
                    collider.vars[f'{kq_knob}']     = collider.vars[f'{kq_knob}_ref']

                    # Adding per-tank corrections
                    for tank in tank_list:
                        collider.vars[f'{kq_knob}.bbcw.{tank}'] = 0 # e.g. kq4.l1b1.bbcw.a

                        # Knobifying to scale with the k1 of the wire
                        #---------------------------------------------
                        collider.vars[f'i_wire.{tank}.{loc}.{beam_name}'] = nominal_current
                        collider.vars[f'd_wire.{tank}.{loc}.{beam_name}'] = nominal_distance
                        nominal_knl_1 = collider.vars[f'knl_1_wire.{tank}.{loc}.{beam_name}']._value
                        nominal_ksl_1 = collider.vars[f'ksl_1_wire.{tank}.{loc}.{beam_name}']._value # should be zero
                        collider.vars[f'i_wire.{tank}.{loc}.{beam_name}'] = parking_current
                        collider.vars[f'd_wire.{tank}.{loc}.{beam_name}'] = parking_distance
                        #--------------------------------------------- 
                        collider.vars[f'{kq_knob}'] += collider.vars[f'{kq_knob}.bbcw.{tank}']*collider.vars[f'knl_1_wire.{tank}.{loc}.{beam_name}']/nominal_knl_1 * collider.vars[f'bbcw_enable_ff_tune']
            #---------------------------------------------

        # Relative limits function
        def get_limits(kq_knob, rel_lim):
                assert rel_lim>0
                ref_value = collider.vars[f'{kq_knob}_ref']._value
                return (-rel_lim*np.abs(ref_value),rel_lim*np.abs(ref_value))

    

        # Preparing the matcher (solve=False)
        #---------------------------------------------

        # Location (start,end) for the matching, will be overwritten in the loop
        opt = {'b1':{'4l1':('s.ds.l1.b1','ip1'), 
                    '4r1':('ip1','e.ds.r1.b1'), 
                    '4l5':('s.ds.l5.b1','ip5'), 
                    '4r5':('ip5','e.ds.r5.b1')},
            'b2':{'4l1':('ip1','s.ds.l1.b2'), 
                    '4r1':('e.ds.r1.b2','ip1'), 
                    '4l5':('ip5','s.ds.l5.b2'), 
                    '4r5':('e.ds.r5.b2','ip5')}}

        # Turning all OFF to get proper targets
        #---------------
        for beam_name in beam_list:
            for loc in loc_list[beam_name]:
                for tank in tank_list:
                    collider.vars[f'i_wire.{tank}.{loc}.{beam_name}'] = 0
                    collider.vars[f'd_wire.{tank}.{loc}.{beam_name}'] = 1
        #---------------
        for beam_name in beam_list:
            #------------------
            _line   = collider[f'lhc{beam_name}']
            _twiss  = _line.twiss4d()

            target_list = [xt.TargetSet(['mux','muy']   , tol=1e-6, value=_twiss, at=xt.END,tag='mu'),
                        xt.TargetSet(['betx','bety'] , tol=1e-6, value=_twiss, at=xt.END,tag='beta'),
                        xt.TargetSet(['alfx','alfy'] , tol=1e-6, value=_twiss, at=xt.END,tag='alpha'),
                        xt.TargetSet(['dx','dpx']    , tol=1e-6, value=_twiss, at=xt.END,tag='disp_x'),
                        xt.TargetSet(['x','y']       , tol=1e-8, value=_twiss, at=xt.END,tag='c.o.')] # c.o. is checked in assert but NOT matched
            #------------------

            for loc in loc_list[beam_name]:
                # Extracting start/end then overwriting
                start,end = opt[beam_name][loc]

                # Preparing vary list
                #---------------------------------------------
                vary_list = []
                for kq in kq_vary_dict.keys():
                    # Skipping if not included
                    if kq_vary_dict[kq]['include'] == False: continue

                    # Per-tank varying knobs
                    kq_knob = f'{kq}.{loc[1:]}{beam_name}'
                    vary_list += [xt.VaryList([f'{kq_knob}.bbcw.{tank}' for tank in tank_list],
                                            step     = kq_vary_dict[kq]['step'],
                                            limits   = get_limits(kq_knob, kq_vary_dict[kq]['rel_lim']),
                                            tag      = f'{kq_knob}.bbcw')]
                #---------------------------------------------

                # Matcher
                #---------------------------------------------
                opt[beam_name][loc] = _line.match(
                    solve   = False, # <- prepare the match without running it
                    start   = start, 
                    end     = end,
                    init    = _twiss, 
                    init_at = xt.START,
                    method  = '4d',
                    vary    = vary_list,
                    targets = target_list)    

                # Disabling all knobs, a priori
                opt[beam_name][loc].disable(vary=True)   

                # Disabling closed orbit targets (only there for inspection)
                opt[beam_name][loc].disable(target=['c.o.'])   
                #---------------------------------------------


        # Powering the wires one-by-one to find the response:
        #-----------------------------------
        # Turning all OFF
        #---------------
        for beam_name in beam_list:
            for loc in loc_list[beam_name]:
                for tank in tank_list:
                    collider.vars[f'i_wire.{tank}.{loc}.{beam_name}'] = 0
                    collider.vars[f'd_wire.{tank}.{loc}.{beam_name}'] = 1
        #---------------

        # Finding the response
        #---------------
        for beam_name in beam_list:
            for loc in loc_list[beam_name]:
                for tank in tank_list:
                    # Powering single wire
                    collider.vars[f'i_wire.{tank}.{loc}.{beam_name}'] = nominal_current
                    collider.vars[f'd_wire.{tank}.{loc}.{beam_name}'] = nominal_distance

                    # assert no change on closed orbit
                    ttt = opt[beam_name][loc].target_status(ret=True)
                    assert np.all(ttt['tol_met'][[('c.o.' in t) for t in ttt['tag']]]), f'Wire bbcw.{tank}.{loc}.{beam_name} seems misaligned!'

                    # Enabling only revelant knobs to vary
                    relevant_fmt = f'{loc[1:]}{beam_name}.bbcw.{tank}' # e.g. xxx.l1b1.bbcw.a
                    opt[beam_name][loc].disable(vary=True)
                    opt[beam_name][loc].enable(vary_name = [vv.name for vv in opt[beam_name][loc].vary if relevant_fmt in vv.name])

                    # Matching
                    opt[beam_name][loc].solve()
                    opt[beam_name][loc].disable(vary=True)

                    # Turning the wire back off.
                    collider.vars[f'i_wire.{tank}.{loc}.{beam_name}'] = 0
                    collider.vars[f'd_wire.{tank}.{loc}.{beam_name}'] = 1
        #---------------

        
        # Going back to parking
        #---------------
        for beam_name in beam_list:
            for loc in loc_list[beam_name]:
                for tank in tank_list:
                    collider.vars[f'i_wire.{tank}.{loc}.{beam_name}'] = parking_current
                    collider.vars[f'd_wire.{tank}.{loc}.{beam_name}'] = parking_distance
        #---------------

        # Adding new knobs for normalized distance (either discarded or not in next generation)
        # -------------------------
        self.add_normalized_distance_knobs(collider)


        # updating closed orbit and beta @ wires
        # -------------------------
        self.update_optics_bbcw(collider)


        # Exporting bbcw knobs to collider metadata
        # -------------------------
        opt_kq_dict = {}
        for beam_name in beam_list:
            opt_kq_dict[beam_name] = {}
            for loc in loc_list[beam_name]:
                opt_kq_dict[beam_name][loc] = opt[beam_name][loc].vary_status(ret=True).to_pandas().to_dict()
        collider.metadata.update(opt_kq_dict)

        return opt


    def add_normalized_distance_knobs(self,collider):
        """
        Adds normalized distance knobs for the wires based on beam parameters.

        Args:
            collider: The collider object to configure.

        Returns:
            None
        """
        # Get the appropriate installation
        beam_list = self.beam_list
        loc_list = self.loc_list
        tank_list = self.tank_list
        bbcw_insert = self.bbcw_insert
        bbcw_orientation_xy = self.bbcw_orientation_xy
        collimation_emittance = self.collimation_emittance
        kq_vary_dict = self.kq_vary_dict

        # Add new knobs for normalized distance (either discarded or not in next generation)
        # ---------------------------- 
        for beam_name in beam_list:
            for loc in loc_list[beam_name]:
                for tank in tank_list:
                    collider.vars[f'dn_wire.{tank}.{loc}.{beam_name}'] = 50
                    
                    # Find out plane of bbcw:
                    _bbcw_name = f'bbcw.{tank}.{loc}.{beam_name}'
                    if bbcw_orientation_xy(_bbcw_name)[0] != 0:
                        # x-plane wire
                        collider.vars[f'd_wire.{tank}.{loc}.{beam_name}'] = collider.vars[f'dn_wire.{tank}.{loc}.{beam_name}'] * collider.vars[f'sigx_wire.{tank}.{loc}.{beam_name}']
                    else:
                        # y-plane wire
                        collider.vars[f'd_wire.{tank}.{loc}.{beam_name}'] = collider.vars[f'dn_wire.{tank}.{loc}.{beam_name}'] * collider.vars[f'sigy_wire.{tank}.{loc}.{beam_name}']





    def update_optics_bbcw(self,collider,_with_checks = False):
        """
        Updates closed orbit and optics parameters at BBCW positions.

        Args:
            collider: The collider object to configure.

        Returns:
            None
        """
        # Get the appropriate installation
        beam_list = self.beam_list
        loc_list = self.loc_list
        tank_list = self.tank_list
        bbcw_insert = self.bbcw_insert
        bbcw_orientation_xy = self.bbcw_orientation_xy
        collimation_emittance = self.collimation_emittance
        kq_vary_dict = self.kq_vary_dict
        
        # Collimation emittance
        #---------------------------
        nemitt_x = collimation_emittance['x']
        nemitt_y = collimation_emittance['y']
        #---------------------------

        for beam_name in beam_list:
            # Twiss for c.o. values
            _line   = collider[f'lhc{beam_name}']
            _twiss  = _line.twiss4d()
            gemittx = ( nemitt_x / _line.particle_ref.beta0[0] / _line.particle_ref.gamma0[0])
            gemitty = ( nemitt_y / _line.particle_ref.beta0[0] / _line.particle_ref.gamma0[0])

            for loc in loc_list[beam_name]:
                for tank in tank_list:
                    _bbcw_name = f'bbcw.{tank}.{loc}.{beam_name}'

                    if _with_checks:
                        # Save original to assert no changes
                        co_x_0= collider.vars[f'co_x_wire.{tank}.{loc}.{beam_name}']._value
                        co_y_0= collider.vars[f'co_y_wire.{tank}.{loc}.{beam_name}']._value
                        sig_x_0= collider.vars[f'sigx_wire.{tank}.{loc}.{beam_name}']._value
                        sig_y_0= collider.vars[f'sigy_wire.{tank}.{loc}.{beam_name}']._value

                    # Update optics
                    collider.vars[f'co_x_wire.{tank}.{loc}.{beam_name}'] = _twiss.rows[_bbcw_name].x[0]
                    collider.vars[f'co_y_wire.{tank}.{loc}.{beam_name}'] = _twiss.rows[_bbcw_name].y[0]

                    collider.vars[f'sigx_wire.{tank}.{loc}.{beam_name}']   = np.sqrt(_twiss.rows[_bbcw_name].betx[0] * gemittx)
                    collider.vars[f'sigy_wire.{tank}.{loc}.{beam_name}']   = np.sqrt(_twiss.rows[_bbcw_name].bety[0] * gemitty) 


                    if _with_checks:
                        # Check
                        assert np.abs(co_x_0 - collider.vars[f'co_x_wire.{tank}.{loc}.{beam_name}']._value) < 1e-6, f'BBCW optics changed since previous generation, {beam_name},{loc}'
                        assert np.abs(co_y_0 - collider.vars[f'co_y_wire.{tank}.{loc}.{beam_name}']._value) < 1e-6, f'BBCW optics changed since previous generation, {beam_name},{loc}'
                        assert np.abs(sig_x_0 - collider.vars[f'sigx_wire.{tank}.{loc}.{beam_name}']._value)/sig_x_0 < 5e-2, f'BBCW optics changed since previous generation, {beam_name},{loc}'
                        assert np.abs(sig_y_0 - collider.vars[f'sigy_wire.{tank}.{loc}.{beam_name}']._value)/sig_y_0 < 5e-2, f'BBCW optics changed since previous generation, {beam_name},{loc}'


    def power_bbcw(self,collider, config_collider):

        # Get the appropriate installation
        beam_list = self.beam_list
        loc_list = self.loc_list
        tank_list = self.tank_list
        bbcw_insert = self.bbcw_insert
        bbcw_orientation_xy = self.bbcw_orientation_xy
        collimation_emittance = self.collimation_emittance
        kq_vary_dict = self.kq_vary_dict
        
        # Get configuration powering
        config_bbcw = config_collider["config_knobs_and_tuning"]["knob_settings"]['bbcw']



        # Choosing either normalized or absolute distance
        if config_bbcw['d_normalized']:
            d_knob = 'dn_wire'
        else:
            d_knob = 'd_wire'


        # Link all tanks to common knob
        for beam_name in beam_list:
            for loc  in loc_list:

                # Define master knobs
                collider.vars[f'i_wire.{loc}.{beam_name}']      = 0
                collider.vars[f'{d_knob}.{loc}.{beam_name}']    = 10 # (either sigma or m...)

                # Link tank knobs
                for tank in tank_list:
                    # Linking currents:
                    collider.vars[f'i_wire.{tank}.{loc}.{beam_name}']   = collider.vars[f'i_wire.{loc}.{beam_name}']
                    # Distance to wire
                    collider.vars[f'{d_knob}.{tank}.{loc}.{beam_name}'] = collider.vars[f'{d_knob}.{loc}.{beam_name}']


        # Power the bbcw and check
        for beam_name in beam_list:
            # Twiss for c.o. values
            _line   = collider[f'lhc{beam_name}']
            _twiss0 = _line.twiss4d()
            for loc  in loc_list:

                _i = config_bbcw[f'i_bbcw_{loc}_{beam_name}']
                _d = config_bbcw[f'd_bbcw_{loc}_{beam_name}']

                # Checking limits on the powering:
                assert np.abs(_i)<1000 , f'Current on the wires are too high, {beam_name},{loc}'
                assert _d>0            , f'Distance of wires should be > 0, {beam_name},{loc}'

                # Power master knobs
                collider.vars[f'i_wire.{loc}.{beam_name}']      = _i
                collider.vars[f'{d_knob}.{loc}.{beam_name}']    = _d

                # twiss to compare
                _twiss1 = _line.twiss4d()

                # Checks
                assert np.std(_twiss1.x-_twiss0.x) < 1e-6                       , f'ff-problem when powering the wires, {beam_name},{loc}'
                assert np.std(_twiss1.y-_twiss0.y) < 1e-6                       , f'ff-problem when powering the wires, {beam_name},{loc}'
                assert np.std((_twiss1.betx-_twiss0.betx)/_twiss0.betx) < 1e-4  , f'ff-problem when powering the wires, {beam_name},{loc}'
                assert np.std((_twiss1.bety-_twiss0.bety)/_twiss0.bety) < 1e-4  , f'ff-problem when powering the wires, {beam_name},{loc}'
                assert np.std(_twiss1.qx-_twiss0.qx) < 1e-5                     , f'ff-problem when powering the wires, {beam_name},{loc}'
                assert np.std(_twiss1.qy-_twiss0.qy) < 1e-5                     , f'ff-problem when powering the wires, {beam_name},{loc}'
                if _i != 0:
                    assert _twiss1.qx != _twiss0.qx                                 , f'broken knobs on the wires..., {beam_name},{loc}'
                    assert _twiss1.qy != _twiss0.qy                                 , f'broken knobs on the wires..., {beam_name},{loc}'

