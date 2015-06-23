#!/bin/bash
curl -s agar.io|grep -Po '(?<=main_out.js\?)[0-9]*'
