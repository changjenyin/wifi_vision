function eigd(folder, output_folder)
	SUB_CNT = 120;
	addpath('dataplot');
	dirlist = dir(folder);

	for i = 3:length(dirlist)
		filename = dirlist(i).name
	
		file = fopen([folder '/' filename]);
		H = fscanf(file, '%f');
		H = reshape(H, size(H, 1) / SUB_CNT, SUB_CNT); % t x sub_carrier
		size(H)

		% Correlation H^TH
		cent_H = H - repmat(mean(H, 1), size(H, 1), 1); % Centralized H
		corr_H = cent_H' * cent_H;

		% Apply eigen value decomposition
		%[D, I] = sort(diag(D), 'descend');
		[V, D] = eig(corr_H);
		D(end, end) = 0;

		% Reconstruct new_H
		recon = V * D * inv(V);
		new_H = pinv(H') * recon;
		
		% Plot old and new H
		cf = 1;
		img = figure(cf);
		result = image(H, 'CDataMapping', 'scaled');
		saveas(img, [output_folder '/' filename '_H.jpg']);
		cf = 2;
		img = figure(cf);
		result = image(new_H, 'CDataMapping', 'scaled');
		saveas(img, [output_folder '/' filename '_newH.jpg']);

		% Close file
		fclose(file);
	end
end
