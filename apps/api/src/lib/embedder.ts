export async function embed(ai: Ai, text: string): Promise<number[]> {
  const response = await ai.run("@cf/baai/bge-small-en-v1.5", {
    text: [text],
  });
  return response.data[0];
}

export function cosineSimilarity(a: number[], b: number[]): number {
  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  const denom = Math.sqrt(normA) * Math.sqrt(normB);
  return denom === 0 ? 0 : dot / denom;
}