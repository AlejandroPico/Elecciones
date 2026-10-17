import { categories } from "../..";
import { axisCalculation, type Answers } from "./model";
import "./Explanation.css";

const decimal = (value: number) =>
  new Intl.NumberFormat("es-ES", { maximumFractionDigits: 2 }).format(value);
const weights = ["", "Normal", "Alta", "Esencial"];
const labels: Record<number, string> = {
  [-2]: "Muy en desacuerdo",
  [-1]: "En desacuerdo",
  0: "Neutral",
  1: "De acuerdo",
  2: "Muy de acuerdo",
};
export default function Explanation({ answers }: { answers: Answers }) {
  return (
    <section className="calculation-explanation">
      <h2>Respuestas y cálculo</h2>
      <p>
        Por eje: 100 × suma de aportaciones ÷ suma de pesos. Cada aportación es
        respuesta ÷ 2 × dirección × importancia. La dirección indica a qué
        extremo del eje conduce estar de acuerdo.
      </p>
      <p>
        Normal pesa 1; alta, 2; esencial, 3. Neutral aporta 0 y conserva su
        peso. Las omisiones y las preguntas pendientes se excluyen. Cada
        pregunta pertenece a un único eje; los temas con más preguntas no añaden
        peso a otros ejes.
      </p>
      {categories.map((category) => (
        <details key={category.id}>
          <summary>{category.name}</summary>
          {category.axes.map((axis) => {
            const calculation = axisCalculation(answers, axis.id);
            return (
              <section className="calculation-axis" key={axis.id}>
                <h3>{axis.name}</h3>
                <p className="calculation-range">
                  −100: {axis.low} · +100: {axis.high}
                </p>
                <ol>
                  {calculation.contributions.map(
                    ({ question, answer, included, numerator }) => (
                      <li key={question.id}>
                        <p>{question.text}</p>
                        <span>
                          {!answer
                            ? "Pendiente"
                            : answer.value === null
                              ? "Omitida · sin peso"
                              : `${question.type === "binary" ? (answer.value > 0 ? "Sí" : "No") : labels[answer.value]} · ${weights[answer.importance].toLowerCase()}`}
                        </span>
                        {included && (
                          <code>
                            {answer.value} ÷ 2 × {question.direction} ×{" "}
                            {answer.importance} = {decimal(numerator)}
                          </code>
                        )}
                      </li>
                    ),
                  )}
                </ol>
                <p className="calculation-total">
                  {calculation.value === null
                    ? "Sin respuestas: este eje no tiene coordenada."
                    : `100 × ${decimal(calculation.numerator)} ÷ ${calculation.weight} = ${decimal(calculation.value)}`}
                </p>
              </section>
            );
          })}
        </details>
      ))}
      <p className="small-note">
        Las coordenadas describen este banco piloto, no una etiqueta ideológica
        absoluta. Una afinidad futura se calculará únicamente sobre preguntas
        comunes con evidencia del programa: 100 × (1 − suma de distancias
        ponderadas ÷ suma de pesos), con distancia = |tu respuesta − posición
        del partido| ÷ 4. Se mostrará siempre su cobertura.
      </p>
    </section>
  );
}
