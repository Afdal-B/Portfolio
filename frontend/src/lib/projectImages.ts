/** Resolves a project's main image: the uploaded one when it exists,
 *  otherwise a Picsum placeholder built from its seed, so a card is never
 *  empty. Cards, the modal hero and its blurred backdrop all use this.
 *
 *  Screenshots get no such fallback on purpose: random stock photos
 *  presented as "screenshots" of a project would be misleading, so the
 *  modal simply hides that section when none were uploaded. */

interface ProjectImages {
  image_url: string
  image_seed: string
}

function placeholder(seed: string, width: number, height: number): string {
  return `https://picsum.photos/seed/${seed}/${width}/${height}`
}

export function mainImage(project: ProjectImages, width: number, height: number): string {
  return project.image_url || placeholder(project.image_seed, width, height)
}
