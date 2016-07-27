%{
	t x d    ->    t x 5
	[data]				[00000]
	[data]				[00000]
	[data]				[00000]
			.							.
			.							.
			.							.
	[data]				[00000]

	(implement by pca())
	[coeff, score, latent] = pca(H, 'VariableWeights', 'variance');
	denoised_H = score(:, start_component, end_component);
%}
function denoised_H = PCA_denoise(H, start_component, end_component, sampling_rate)
	denoised_H = [];

	cent_H = H - repmat(mean(H, 1), size(H, 1), 1); % Centralized H
	idx = 1;
	while idx + sampling_rate / 2 <= size(cent_H, 1) % abandom if last part is less than 0.5 sec
		% Cut 1sec H (if less than 1sec, cut to end)
		if idx + sampling_rate > size(cent_H, 1)
			H_1sec = cent_H(idx:end, :);
		else
			H_1sec = cent_H(idx:idx + sampling_rate - 1, :);
		end

		% Correlation H^TH
		%corr_H = corrcoef(H_1sec);
		corr_H = H_1sec' * H_1sec;
		if find(isnan(corr_H))
			denoised_H = 'has_nan';
			return
		end

		% Compute and sort eigenvectors
		[V, D] = eig(corr_H);
		[D, I] = sort(diag(D), 'descend');
		transMatrix = V(:, I(start_component:end_component, 1));
	
		% Get principle components -> Concate to output
		denoised_H = [denoised_H; H_1sec * transMatrix];

		idx = idx + sampling_rate;
	end
end
