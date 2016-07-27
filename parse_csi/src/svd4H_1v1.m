function svd4H(folder, output_folder, width, height, NUM_ANT_PAIR)
	if ~exist('NUM_ANT_PAIR', 'var')
		NUM_ANT_PAIR = 4;
	end
	SUB_CNT = NUM_ANT_PAIR*30;
	parts = strsplit(folder, '/');
	SV_feat_folder = strcat('/tmp4/transfer/WiSee/new_intel_csi/signal_process/feature/singular_value/', parts(end));
	SV_feat_folder = SV_feat_folder{1};

	dirlist = dir(folder);

	SV = []; names = {};
	%orig_H_min = repmat(Inf, 1, 4); orig_H_max = repmat(-Inf, 1 ,4);
	vmins = {[],[],[],[]}; vmaxs = {[],[],[],[]};
	new_H_min  = repmat(Inf, 1, 4); new_H_max  = repmat(-Inf, 1, 4);
	for i = 3:length(dirlist)
		filename = dirlist(i).name;

		parts = strsplit(filename, '.');
		names{end+1} = parts(1);
		if strcmp(filename, 'all') || strcmp(filename, 'avg')
			continue
		end

		load([folder '/' filename]);
		H = ori_mat';
		for j = 1:NUM_ANT_PAIR
			% Apply SVD on H_part
			H_part = H(:, (j - 1) * 30 + 1:j * 30);
			[U, S, V] = svd(H_part, 'econ');
			S(1, 1) = 0; % remove 1st SV
			new_H_part = U * S * V'; % Reconstruct new_H_part

			isComplex = ~isreal(new_H_part);
			if isComplex
				vmin = min(min(min(abs(new_H_part))));
				vmax = max(max(max(abs(new_H_part))));
			else
				vmin = min(min(min(new_H_part)));
				vmax = max(max(max(new_H_part)));
			end

			vmins{j} = [vmins{j}, vmin]; 
			vmaxs{j} = [vmaxs{j}, vmax]; 
			
			if vmin < new_H_min(1, j)
				new_H_min(1, j) = vmin;
			end

			if vmax > new_H_max(1, j)
				new_H_max(1, j) = vmax;
			end
		end
	end
	write_sv_to_file(SV, names, SV_feat_folder);

	for i = 3:length(dirlist)
		filename = dirlist(i).name
		% Ignore other files
		if strcmp(filename, 'all') || strcmp(filename, 'avg')
			continue
		end

		% Read in H as t x SUB_CNT
		load([folder '/' filename]);
		H = ori_mat';

		% Save original imgs
		cf = 1;
		img = figure(cf);

		if ~exist([output_folder '/orig'])
			mkdir([output_folder '/orig']);
		end	

		if isComplex
			result = image(abs(H), 'CDataMapping', 'scaled');
		else
			result = image(H, 'CDataMapping', 'scaled');
		end
		saveas(img, [output_folder '/orig/' filename '_H.jpg']);

		% Save SVDed antenna pair img
		for j = 1:NUM_ANT_PAIR
			% Apply SVD on H_part
			H_part = H(:, (j - 1) * 30 + 1:j * 30);
			[U, S, V] = svd(H_part, 'econ');
			S(1, 1) = 0; % remove 1st SV
			new_H_part = U * S * V'; % Reconstruct new_H_part

			% Output for training
			action = strsplit(filename, '.');
			mkdir([output_folder '/' action{1}]);

			cf = 1;
			for i = 1:NUM_ANT_PAIR
				img = figure(cf);
				if isComplex
					result = image(abs(new_H_part), 'CDataMapping', 'scaled');
				else
					result = image(new_H_part, 'CDataMapping', 'scaled');
				end
		   		set(gca, 'position', [0 0 1 1], 'units', 'normalized');
				set(gca, 'CLim', [new_H_min(1, i), new_H_max(1, i)]);
			   	axis off;
				res = get(0, 'screenpixelsPerInch');
				pSize = [width, height] / res;
			    set(gcf,'PaperUnits','inches')
				set(gcf,'PaperSize', pSize)
				set(gcf,'PaperPosition',[1 1 pSize(1) pSize(2)]);
				set(gcf,'PaperPositionMode', 'manual')
		   		print('-djpeg', [output_folder '/' action{1} '/' num2str(i)], sprintf('-r%d', res));

				clf;
				cf = cf + 1;
			end
		end
	end
end
