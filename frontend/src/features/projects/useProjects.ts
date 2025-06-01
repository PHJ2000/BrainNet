// features/projects/useProjects.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchProjects, createProject } from "./projectApi";

export const useProjects = () => {
  return useQuery({ queryKey: ["projects"], queryFn: fetchProjects });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createProject,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    }
  });
};
