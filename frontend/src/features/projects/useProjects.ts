// // features/projects/useProjects.ts
// import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
// import { fetchProjects, createProject } from "./projectApi";

// export const useProjects = () => {
//   return useQuery({ queryKey: ["projects"], queryFn: fetchProjects });
// };

// export const useCreateProject = () => {
//   const queryClient = useQueryClient();
//   return useMutation({
//     mutationFn: createProject,
//     onSuccess: () => {
//       queryClient.invalidateQueries({ queryKey: ["projects"] });
//     }
//   });
// };

// features/projects/useProjects.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {apiClient} from "@/lib/apiClient";

export const useProjects = () => {
  return useQuery({
    queryKey: ["projects"],
    queryFn: async () => {
      const res = await apiClient.get("/projects");
      return res.data;
    },
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ name, description }: { name: string; description?: string }) => {
      const res = await apiClient.post("/projects", { name, description });
      return res.data;
    },
    onSuccess: () => {
      // ✅ 캐시 무효화 → ProjectList가 자동 갱신됨
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
};
