# dir=$(pwd)

# vtune_dir=$dir/applications.analyzers.vtune
# patch_dir=$dir/code_coverage

# Apply curl patch
cd $vtune_dir/vcs/curl8
patch -p1 < $patch_dir/patches/curl.patch
# Apply libarchive patch
cd $vtune_dir/vcs/libarchive3/
patch -p1 < $patch_dir/patches/libarchive.patch
# Apply libunwind patch
cd $vtune_dir/vcs/libunwind0/
patch -p1 < $patch_dir/patches/libunwind.patch
# Apply perftestapps.patch
cd $vtune_dir/vcs/perftestapps1/
patch -p1 < $patch_dir/patches/perftestapps.patch
# Apply tpss.patch
cd $vtune_dir/vcs/tpss2/
patch -p1 < $patch_dir/patches/tpss.patch
# Apply deinterface.patch
cd $vtune_dir/vcs/dbinterface1/
patch -p1 < $patch_dir/patches/dbinterface.patch
# Apply samplingmrte.patch
cd $vtune_dir/vcs/samplingmrte1/
patch -p1 < $patch_dir/patches/samplingmrte.patch