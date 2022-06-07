+++
title = "Terraphim Config structure"
description = "Terraphim config structure"
date = 2022-02-21
[taxonomies]
categories = ["Documentation"]
tags = ["terraphim", "config","plugins"]

[extra]
comments = false
+++

# Terraphim config structure

Most of the functionality is driven from the config file.

### [global]

section for global parameters - like global shortcuts

### [[roles]]
Roles are the separate abstract layers and define behaviour of the search for particular role. It's roughly following roles definition from ISO 42010 and other systems engineering materials and at different point in time one can wear diferent heat (different role). For example I can be engineer, architect, father or gamer. In each of those roles I will have a different concenrns which are driving different relevance and UX requirements. 

Each role have a 
* name, 
* Theme
* Relevance function 
* plugins 
and (set of) plugins, which are providing data sources. 
The concept roughly follows Model (data sources and mapper), ViewModel (with relevance function) and View (with UI).

