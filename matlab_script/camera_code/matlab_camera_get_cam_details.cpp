#include "VisionManager.h"

#include <vector>
#include <stdio.h>

int main()
{
	VisionManager VisManager = VisionManager();

	int count = VisManager.get_nr_of_devices();
	
	printf("#1 %d\n", count);


	for (int i = 0; i < count; i++)
	{
		rs2_intrinsics intrinsics = VisManager.get_intrinsics_from_device(i);

		//printf("#2 %s\n", serials[i]);
		/* center of projection x */
		printf("#3 %f\n", intrinsics.ppx);
		/* center of projection y */
		printf("#4 %f\n", intrinsics.ppy);
		/* focal length x */
		printf("#5 %f\n", intrinsics.fx);
		/* focal length y */
		printf("#6 %f\n", intrinsics.fy);
		/*image rows */
		printf("#7 %d\n", intrinsics.width);
		/* image columns */
		printf("#8 %d\n", intrinsics.height);
		/* distoprtion_model */
		printf("#9 %s\n", rs2_distortion_to_string(intrinsics.model));
		/* image columns */
		for (int i = 0; i < 5; i++)
		{
			printf("#1%d %f\n", i, intrinsics.coeffs[i]);
		}
		
	}

	return 1;
}
