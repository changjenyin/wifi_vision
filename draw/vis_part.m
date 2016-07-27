function vis_parts(dir_path, img_dir, width, height)
	addpath('lib');

	SUB_CNT = 30;
	dirlist = dir(dir_path);
	mkdir(img_dir);

	for x = 3:length(dirlist)
	    dirlist(x).name
	    mkdir([img_dir '/' dirlist(x).name]);
	
			%Process for each ant
	    filelist = dir([dir_path '/' dirlist(x).name]);

			tmp_mats = [];
			ori_filenames = [];
			f_idx = 0;
	    for y = 3:length(filelist)
	        current_file = filelist(y).name;
	        if strcmp(current_file, 'avg') == 1
	            continue;
	        end
					f_idx = f_idx + 1;

	        [pathstr, file_name, ext] = fileparts(current_file);
	        [xxx, ori_filename, xxx] = fileparts(file_name);
					ori_filenames(end+1) = ori_filename;
	        
	        csi_f = fopen([dir_path '/' dirlist(x).name '/' current_file]);
	        tmp_mat = fscanf(csi_f, '%f');
	        tmp_mat = reshape(tmp_mat, size(tmp_mat, 1) / SUB_CNT, SUB_CNT)';

					% Subtract each sub-carriers mean
					%tmp_mat = subtractMean(tmp_mat);
					%mean_list = mean(tmp_mat, 2);
					%mean_list = repmat(mean_list, 1, size(tmp_mat, 2));
					%tmp_mat = tmp_mat - mean_list;
	
	        %Low-pass
					tmp_mat = low_pass(1000, 50, tmp_mat);
	
	        %Signal conditioning
					tmp_mat = avg_window(300, tmp_mat);
					
					%sub-wise normalization
					%tmp_mat = subcarrier_norm(tmp_mat);

					tmp_mats(:,:,f_idx) = tmp_mat;
			end

			vmin = min(min(min(tmp_mats)))
			vmax = max(max(max(tmp_mats)))
			for i = 1:f_idx
	          
	        %Print extend or original
	        cf = 1;
	        img = figure(cf);
	        result = image(tmp_mats(:,:,i), 'CDataMapping', 'scaled');
					%colormap(gray(256));
	        %set(gca, 'CLim', [0, 80]);
	        set(gca, 'CLim', [vmin, vmax]);
	        set(gca, 'position', [0 0 1 1], 'units', 'normalized');
	        %colormap('default');
	        %colorbar;
	        axis off;
	        %saveas(img, ['/tmp4/transfer/WiSee/intel_csi/imgs/R544/' dirlist(x).name '/' ori_filename], 'jpg');
	
					res = get(0, 'screenpixelsPerInch');
					%pSize = [size(tmp_mat, 2), size(tmp_mat, 1)] / res;
					pSize = [width, height] / res;
	        set(gcf,'PaperUnits','inches')
					set(gcf,'PaperSize', pSize)
					set(gcf,'PaperPosition',[1 1 pSize(1) pSize(2)]);
					set(gcf,'PaperPositionMode', 'manual')

	        [img_dir '/' dirlist(x).name '/' ori_filenames(i)]
	        print('-djpeg', [img_dir '/' dirlist(x).name '/' ori_filenames(i)], sprintf('-r%d', res));
	 
	        %visualize one sub-carrier
	        %cf = 2;
	        %f2 = figure(cf);
	        %plot(tmp_mat(3, :));
	        %saveas(f2, ['/tmp4/transfer/WiSee/intel_csi/parse_csi/one_csi' dirlist(x).name '/' ori_filename], 'jpg');
	    end
	end
end
