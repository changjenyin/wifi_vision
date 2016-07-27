function vis_whole(dir_path, out_dir)
	addpath('lib');
	addpath('/tmp4/transfer/WiSee/intel_csi/parse_csi/plot2svg_20120915/plot2svg_20120915')

	SUB_CNT = 120;
	CHANNEL_CNT = 4;
	dirlist = dir(dir_path);
	
	mkdir(out_dir);
	for x = 3:length(dirlist)
	    current_file = dirlist(x).name
	
	    [pathstr, file_name, ext] = fileparts(current_file);
	    [xxx, ori_filename, xxx] = fileparts(file_name);
	   
	    csi_f = fopen([dir_path '/' current_file]);
	    tmp_mat = fscanf(csi_f, '%f');
	    tmp_mat = reshape(tmp_mat, size(tmp_mat, 1) / SUB_CNT, SUB_CNT)';

			%Remove DC
			%tmp_mat = removeDCBySettingZero(tmp_mat);
	
	    %Low-pass
			tmp_mat = low_pass(1000, 50, tmp_mat);
	
	    %Signal conditioning
			tmp_mat = avg_window(300, tmp_mat);

			%sub-wise normalization
			%tmp_mat = subcarrier_norm(tmp_mat);

			anchor = 1;
			step = SUB_CNT/CHANNEL_CNT;
		
	    img = figure();
			for i = 1:CHANNEL_CNT 

				bound = anchor+step-1;
				mat = tmp_mat(anchor:bound, :);
				vmin = min(min(mat));
				vmax = max(max(mat));
	    	  
				if i ~= 5
					h = axes;
	    		result = image(mat, 'CDataMapping', 'scaled');
					%colormap(gray(256));

	    		set(h, 'CLim', [vmin, vmax]);
					set(h, 'units', 'normalized');
	    		set(h, 'Position', [0 1-bound/SUB_CNT 1 step/SUB_CNT]);
	    		axis off;
				end
				anchor = anchor + step;
			end
			%saveas(img, [out_dir '/' file_name], 'jpg');
			plot2svg([out_dir '/' file_name '.svg'], img)
	end
end 
