#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.crs as ccrs
from cartopy import feature as cf

def cart_plot(axes,ix, ncols=3,nrows=3, rlon=-150,llon=-60,tlat=42,blat=15,projection=ccrs.PlateCarree()):
    #axes.add_feature(cf.BORDERS,linewidth=0.05) #add features (boarders )
    axes.add_feature(cf.COASTLINE,linewidth=1,color='gray') #coastlines 
    gl=axes.gridlines(crs=projection, draw_labels=True, linewidth=0.5, color='gray', alpha=0.01, linestyle='--') #create the map type with grids 
    axes.set_extent([llon,rlon,blat,tlat]) #set the extent of the map
    if ix%ncols ==0:
        
        gl.top_labels = False; gl.left_labels = True #set which axis labels should show 
        gl.right_labels=False; gl.xlines = False; gl.bottom_labels=False

    elif ix>=(ncols*nrows)-ncols:
        gl.top_labels = False; gl.left_labels = False #set which axis labels should show 
        gl.right_labels=False; gl.xlines = False; gl.bottom_labels=True

    else:
        gl.top_labels = False; gl.left_labels = False #set which axis labels should show 
        gl.right_labels=False; gl.xlines = False; gl.bottom_labels=False
    if ix == (ncols*nrows)-ncols:
        gl.top_labels = False; gl.left_labels = True #set which axis labels should show 
        gl.right_labels=False; gl.xlines = False; gl.bottom_labels=True
    axes.xformatter = LONGITUDE_FORMATTER;  axes.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'color':'black','size':12} #change font style for x-axis 
    gl.ylabel_style = {'color':'black','size':12}#change font style for y-axis  