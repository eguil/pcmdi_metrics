def model_land_mask_out(mip,model,model_timeseries):
  import numpy as NP
  #-------------------------------------------------
  # Extract SST (mask out land region)
  #- - - - - - - - - - - - - - - - - - - - - - - - -
  # Read model's land fraction
  model_lf_path = get_latest_pcmdi_mip_lf_data_path(mip,model,'sftlf')
  #model_lf_path = '/work/cmip5/fx/fx/sftlf/cmip5.'+model+'.historical.r0i0p0.fx.atm.fx.sftlf.ver-1.latestX.xml'
  f_lf = cdms.open(model_lf_path)
  lf = f_lf('sftlf')

  # Check land fraction variable to see if it meets criteria (0 for ocean, 100 for land, no missing value)
  lf[ lf == lf.missing_value ] = 0
  if NP.max(lf) == 1.:
    lf = lf * 100

  # Matching dimension
  model_timeseries, lf_timeConst = genutil.grower(model_timeseries, lf)

  #opt1 = True
  opt1 = False

  if opt1: # Masking out partial land grids as well
    model_timeseries_masked = NP.ma.masked_where(lf_timeConst>0, model_timeseries) # mask out land even fractional (leave only pure ocean grid)
  else: # Masking out only full land grid but use weighting for partial land grids
    model_timeseries_masked = NP.ma.masked_where(lf_timeConst==100, model_timeseries) # mask out pure land grids
    lf2 = (100.-lf)/100.
    model_timeseries,lf2_timeConst = genutil.grower(model_timeseries,lf2) # Matching dimension
    model_timeseries_masked = model_timeseries_masked * lf2_timeConst # consider land fraction like as weighting

  # Retrive dimension coordinate ---

  time = model_timeseries.getTime()
  lat = model_timeseries.getLatitude()
  lon = model_timeseries.getLongitude()

  model_timeseries_masked.setAxis(0,time)
  model_timeseries_masked.setAxis(1,lat)
  model_timeseries_masked.setAxis(2,lon)

  model_timeseries = model_timeseries_masked

  return(model_timeseries)
