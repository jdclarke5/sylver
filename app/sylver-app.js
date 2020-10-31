import {LitElement, html, css} from "lit-element";

export class SylverApp extends LitElement {

  static get properties() {
    return {
      inputString: {type: String},
      input: {type: Array},
      length: {type: Number},
      position: {type: Object},
      history: {type: Array},
    };
  }

  static get styles() {
    return css`

      #input[input-invalid] {
        border: 1px solid red;
      }

      .row {
        white-space: nowrap;
      }

      .cell {
        display: inline-block;
        width: 16px;
        height: 16px;
        background-color: black;
        border: 1px solid #484848;
        border-radius: 4px;
        margin: 4px;
        padding: 1px;
        font-size: 0.55em;
      }

      .cell[gap] {
        background-color: #646464;
        cursor: pointer;
      }
      .cell[generator] {
        background-color: #242424;
      }
      
      .status-indicator {
        display: none;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        position: absolute;
        transform: translate(13px, -5px);
      }

      .status-indicator[status="P"] {
        display: block;
        background-color: green;
      }

      .status-indicator[status="N"] {
        display: block;
        background-color: red;
      }

    `;
  }

  renderArray(position) {
    // Create cells
    let cells = position.bitarray.map( (bool, i) => html`
      <div class="cell"
        @click=${!bool ? this.handleClick : null}
        .number=${i}
        ?generator=${position.generators.includes(i)}
        ?gap="${!bool}">
        <div class="status-indicator" 
          status="${position.children && position.children[i] ? position.children[i].status : null}">
        </div>
        ${i}
      </div>
    `);
    let nRows = position.multiplicity;
    let rows = [];
    for (let i = 0; i < nRows; i++) {rows.push(html`
      ${cells.filter((e, j) => j % nRows === i)}
    `)}
    return rows.map(row => html`
      <div class="row">
        ${row}
      </div>
    `)
  }

  render() {

    return html`
      <main>

        <div id="info-panel">
          <input type="number" min="100" step="1" .value="${this.length}"
            @input=${e => this.length = e.target.value}>
          <input id="input" type="text" .value="${this.inputString}" 
            @input=${this.onInputChange} 
            ?input-invalid="${this.input.find(el => !Number.isInteger(el)) !== undefined}">
          <button @click=${this.getPosition}>Hi Ho Sylver!</button>
          <button @click=${this.handleUndo}>Undo</button>
          <div>
            Position: ${this.position ? this.position.name : null}
            GCD: ${this.position? this.position.gcd: null}
            Frobenius: ${this.position ? this.position.frobenius : null}
            Irreducible? ${this.position ? this.position.irreducible === "s" ? "quiet ender"
              : this.position.irreducible === "p" ? "ender" : "no" : null}
            Status: ${this.position ? this.position.status : null}
          </div>
        </div>

        <div id="viz">
          ${this.position ? this.renderArray(this.position) : null}
        </div>

      </main>
    `;
  }

  constructor() {
    super();
    this.inputString = "9,11";
    this.input = [9, 11];
    this.length = 100;
    this.position = null;
    this.history = [];
  }

  onInputChange(e) {
    this.inputString = e.target.value;
    this.input = this.inputString.split(",").map(Number);
  }

  handleUndo() {
    if (this.history.length === 1) {
      return
    }
    this.history.pop();
    let previousInput = this.history.slice(-1).pop();
    this.inputString = previousInput;
    this.input = this.inputString.split(",").map(Number);
    this.getPosition();
  }

  handleClick(e) {
    let number = e.target.number;
    if (!number) {
      return
    }
    this.inputString = `${this.inputString},${number}`;
    this.input = [...this.input, number];
    this.getPosition();
  }

  getPosition() {
    let url = new URL("/api/get", window.location.origin);
    url.searchParams.append("length", this.length);
    url.searchParams.append("input", this.input);
    url.searchParams.append("children", true);
    fetch(url, {
      method: "GET",
    })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        console.log(data);
        return;
      }
      this.position = data;
      if (this.inputString != this.history.slice(-1).pop()) {
        this.history = [...this.history, this.inputString];
      }
    })
  }

}

window.customElements.define("sylver-app", SylverApp);
